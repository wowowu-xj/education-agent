# -*- coding: utf-8 -*-
"""障碍诊断 API。

覆盖 design D5–D7：批量 LLM 诊断（run-llm）、班级障碍分布查询（barrier）、
教师覆盖（override）、阈值配置（config）、班级统计 / 知识点分析 / 学生历史
三个查询端点。

数据隔离：普通教师仅见任课班级（TeacherClassSubject）与自有考试（Paper）。
"""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, ConfigDict
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_teacher
from app.core.database import get_db
from app.core.enums import BarrierType, MisconceptionCategory
from app.models import (
    BarrierConfig,
    DiagnosisOverrideLog,
    Exam,
    Paper,
    Question,
    Student,
    StudentAnswer,
    Teacher,
    TeacherClassSubject,
)
from app.models.base import utcnow
from chem_skills.chemistry_diagnosis.engine.aggregator import (
    BARRIER_KEYS,
    build_barrier_profile,
    build_misconception_profile,
    dominant,
    knowledge_points_for,
)
from chem_skills.chemistry_diagnosis.engine.diagnosis import (
    DiagnosisEngine,
    DiagnosisInput,
)
from chem_skills.chemistry_diagnosis.engine.llm_client import DashScopeDiagnosisClient

router = APIRouter(tags=["诊断"], prefix="/api/diagnosis")


# ---------------------------------------------------------------------------
# 诊断引擎注入缝（测试经 dependency_overrides 注入 FakeLLM）
# ---------------------------------------------------------------------------

_engine: DiagnosisEngine | None = None


def get_diagnosis_engine() -> DiagnosisEngine:
    """返回进程级诊断引擎单例（惰性构建）。"""
    global _engine
    if _engine is None:
        _engine = DiagnosisEngine(DashScopeDiagnosisClient())
    return _engine


# ---------------------------------------------------------------------------
# 通用工具
# ---------------------------------------------------------------------------


def _get_owned_exam(db: Session, exam_id: int, teacher_id: int) -> Exam:
    """按 id + 教师归属取考试（经 Paper 隔离），不存在则 404。"""
    exam = db.execute(
        select(Exam)
        .join(Paper, Paper.id == Exam.paper_id)
        .where(
            Exam.id == exam_id,
            Paper.teacher_id == teacher_id,
            Paper.deleted_at.is_(None),
        )
    ).scalar_one_or_none()
    if exam is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "考试不存在"},
        )
    return exam


def _teacher_teaches_class(db: Session, teacher_id: int, class_id: int) -> bool:
    """教师是否任课该班级。"""
    return (
        db.execute(
            select(TeacherClassSubject.id).where(
                TeacherClassSubject.teacher_id == teacher_id,
                TeacherClassSubject.class_id == class_id,
            ).limit(1)
        ).scalar_one_or_none()
        is not None
    )


def _misconception(value: str | None) -> MisconceptionCategory | None:
    """把迷思概念字符串转枚举（None 透传）。"""
    return MisconceptionCategory(value) if value else None


def _refresh_student_profile(db: Session, student_id: int) -> None:
    """从学生全部已诊断错误作答聚合双维度画像并写回 Student。

    覆盖 design D6 与 spec「学生画像聚合」：按 barrier_type 与
    misconception_category 分别计数归一化、补齐缺失类型为 0，
    写 ``Student.barrier_profile`` / ``Student.misconception_profile``，
    并刷新 ``barrier_updated_at``。
    """
    answers = db.execute(
        select(StudentAnswer).where(
            StudentAnswer.student_id == student_id,
            StudentAnswer.is_correct == False,  # noqa: E712
            StudentAnswer.barrier_type.isnot(None),
        )
    ).scalars().all()

    student = db.get(Student, student_id)
    if student is None:
        return
    student.barrier_profile = build_barrier_profile(
        [a.barrier_type for a in answers]
    )
    student.misconception_profile = build_misconception_profile(
        [a.misconception_category for a in answers]
    )
    student.barrier_updated_at = utcnow()


# ---------------------------------------------------------------------------
# Pydantic 模型
# ---------------------------------------------------------------------------


class RunLLMResponse(BaseModel):
    """批量诊断结果。"""

    analyzed_count: int
    failed_count: int


class StudentBarrierOut(BaseModel):
    """班级障碍分布里的单个学生。"""

    student_id: int
    student_name: str
    dominant_barrier: str | None
    weak_knowledge_points: list[str]


class BarrierDistributionResponse(BaseModel):
    """班级障碍分布响应。"""

    students: list[StudentBarrierOut]
    class_barrier_distribution: dict[str, int]


class OverrideRequest(BaseModel):
    """教师覆盖请求。"""

    barrier_type: BarrierType
    reason: str


class OverrideResponse(BaseModel):
    """教师覆盖响应。"""

    student_id: int
    barrier_profile: dict[str, float]


class BarrierConfigOut(BaseModel):
    """阈值配置响应。"""

    model_config = ConfigDict(from_attributes=True)

    concept_threshold: int
    reading_threshold: int
    expression_threshold: int
    mastery_threshold: int
    auto_sync_to_student: bool


class BarrierConfigUpdate(BaseModel):
    """阈值配置更新（部分字段可选）。"""

    concept_threshold: int | None = None
    reading_threshold: int | None = None
    expression_threshold: int | None = None
    mastery_threshold: int | None = None
    auto_sync_to_student: bool | None = None


class ClassStatsResponse(BaseModel):
    """班级统计响应。"""

    student_count: int
    answer_count: int
    barrier_distribution: dict[str, int]


class KpAnalysisResponse(BaseModel):
    """知识点障碍分析响应。"""

    knowledge_point: str
    error_rate: float
    barrier_distribution: dict[str, int]


class StudentHistoryOut(BaseModel):
    """学生诊断历史（按考试分组）。"""

    exam_id: int
    accuracy: float
    barrier_distribution: dict[str, int]


# ---------------------------------------------------------------------------
# 端点
# ---------------------------------------------------------------------------


@router.post("/run-llm/{exam_id}", response_model=RunLLMResponse, summary="批量 LLM 诊断")
def run_llm(
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
    engine: DiagnosisEngine = Depends(get_diagnosis_engine),
) -> RunLLMResponse:
    """对一次考试最多 10 条未诊断错误作答执行三引擎诊断并写回。

    返回 analyzed_count（成功写回条数）与 failed_count（LLM 失败由规则兜底条数）。
    """
    _get_owned_exam(db, exam_id, teacher.id)

    rows = db.execute(
        select(StudentAnswer, Question.content)
        .join(Question, Question.id == StudentAnswer.question_id)
        .where(
            StudentAnswer.exam_id == exam_id,
            StudentAnswer.is_correct == False,  # noqa: E712
            StudentAnswer.barrier_type.is_(None),
        )
        .order_by(StudentAnswer.id)
        .limit(10)
    ).all()

    if not rows:
        return RunLLMResponse(analyzed_count=0, failed_count=0)

    inputs = [
        DiagnosisInput(student_answer=answer.student_answer, question_text=content)
        for answer, content in rows
    ]
    outcomes = engine.diagnose_many(inputs)

    analyzed_count = 0
    failed_count = 0
    diagnosed_student_ids: set[int] = set()
    for (answer, _), outcome in zip(rows, outcomes):
        fusion = outcome.fusion
        if fusion.barrier_type is None:
            # 规则与 LLM 均无信号，保持未诊断
            continue
        answer.barrier_type = fusion.barrier_type
        answer.misconception_category = _misconception(fusion.misconception_category)
        answer.confidence = fusion.confidence
        diagnosed_student_ids.add(answer.student_id)
        analyzed_count += 1
        if outcome.llm_failed:
            failed_count += 1

    # 聚合写回受影响学生的双维度画像（design D6 / spec「学生画像聚合」）
    for student_id in diagnosed_student_ids:
        _refresh_student_profile(db, student_id)

    db.commit()
    return RunLLMResponse(analyzed_count=analyzed_count, failed_count=failed_count)


@router.get(
    "/barrier/{class_id}/{exam_id}",
    response_model=BarrierDistributionResponse,
    summary="班级障碍分布",
)
def barrier_distribution(
    class_id: int,
    exam_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> BarrierDistributionResponse:
    """某班某次考试的学生主导障碍 + 班级三障碍类型人数分布。"""
    _get_owned_exam(db, exam_id, teacher.id)

    rows = db.execute(
        select(StudentAnswer, Student)
        .join(Student, Student.id == StudentAnswer.student_id)
        .where(
            StudentAnswer.exam_id == exam_id,
            Student.class_id == class_id,
            StudentAnswer.is_correct == False,  # noqa: E712
            StudentAnswer.barrier_type.isnot(None),
            Student.deleted_at.is_(None),
        )
    ).all()

    by_student: dict[int, dict] = {}
    for answer, student in rows:
        entry = by_student.setdefault(
            student.id,
            {"student": student, "barriers": [], "misconceptions": []},
        )
        entry["barriers"].append(answer.barrier_type)
        if answer.misconception_category is not None:
            entry["misconceptions"].append(answer.misconception_category.value)

    students_out: list[StudentBarrierOut] = []
    distribution = {k: 0 for k in BARRIER_KEYS}
    for student_id in sorted(by_student):
        entry = by_student[student_id]
        dom = dominant(build_barrier_profile(entry["barriers"]))
        students_out.append(
            StudentBarrierOut(
                student_id=student_id,
                student_name=entry["student"].name,
                dominant_barrier=dom,
                weak_knowledge_points=knowledge_points_for(entry["misconceptions"]),
            )
        )
        if dom:
            distribution[dom] += 1

    return BarrierDistributionResponse(
        students=students_out,
        class_barrier_distribution=distribution,
    )


@router.put("/override/{student_id}", response_model=OverrideResponse, summary="教师覆盖画像")
def override_student(
    student_id: int,
    payload: OverrideRequest,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> OverrideResponse:
    """教师以指定类型覆盖学生障碍画像（90/5/5），并记录审计日志。"""
    student = db.execute(
        select(Student).where(
            Student.id == student_id, Student.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "学生不存在"},
        )
    if not _teacher_teaches_class(db, teacher.id, student.class_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "无权覆盖该学生画像"},
        )

    old_profile = student.barrier_profile
    new_profile = {k: 0.05 for k in BARRIER_KEYS}
    new_profile[payload.barrier_type.value] = 0.9

    db.add(
        DiagnosisOverrideLog(
            student_id=student.id,
            old_profile=old_profile,
            new_profile=new_profile,
            reason=payload.reason,
            operator_id=teacher.id,
        )
    )
    student.barrier_profile = new_profile
    student.barrier_updated_at = utcnow()
    db.commit()

    return OverrideResponse(student_id=student.id, barrier_profile=new_profile)


@router.get("/config/{teacher_id}", response_model=BarrierConfigOut, summary="获取阈值配置")
def get_config(
    teacher_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> BarrierConfigOut:
    """获取教师阈值配置，无历史记录时返回默认值。"""
    if teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "只能管理自己的配置"},
        )
    cfg = db.execute(
        select(BarrierConfig).where(BarrierConfig.teacher_id == teacher_id)
    ).scalar_one_or_none()
    if cfg is None:
        return BarrierConfigOut(
            concept_threshold=3,
            reading_threshold=2,
            expression_threshold=3,
            mastery_threshold=3,
            auto_sync_to_student=False,
        )
    return cfg


@router.put("/config/{teacher_id}", response_model=BarrierConfigOut, summary="更新阈值配置")
def put_config(
    teacher_id: int,
    payload: BarrierConfigUpdate,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> BarrierConfigOut:
    """upsert 教师阈值配置。"""
    if teacher_id != teacher.id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "只能管理自己的配置"},
        )
    cfg = db.execute(
        select(BarrierConfig).where(BarrierConfig.teacher_id == teacher_id)
    ).scalar_one_or_none()
    if cfg is None:
        cfg = BarrierConfig(teacher_id=teacher_id)
        db.add(cfg)

    updates = payload.model_dump(exclude_unset=True)
    for key, value in updates.items():
        setattr(cfg, key, value)

    db.commit()
    db.refresh(cfg)
    return cfg


@router.get("/class/{class_id}/stats", response_model=ClassStatsResponse, summary="班级统计")
def class_stats(
    class_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> ClassStatsResponse:
    """班级已诊断错误作答的障碍分布统计。"""
    if not _teacher_teaches_class(db, teacher.id, class_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "无权查看该班级"},
        )

    rows = db.execute(
        select(StudentAnswer)
        .join(Student, Student.id == StudentAnswer.student_id)
        .where(
            Student.class_id == class_id,
            StudentAnswer.is_correct == False,  # noqa: E712
            StudentAnswer.barrier_type.isnot(None),
            Student.deleted_at.is_(None),
        )
    ).scalars().all()

    student_ids = {a.student_id for a in rows}
    distribution = {k: 0 for k in BARRIER_KEYS}
    for a in rows:
        distribution[a.barrier_type.value] += 1

    return ClassStatsResponse(
        student_count=len(student_ids),
        answer_count=len(rows),
        barrier_distribution=distribution,
    )


@router.get(
    "/class/{class_id}/kp/{kp}",
    response_model=KpAnalysisResponse,
    summary="知识点障碍分析",
)
def kp_analysis(
    class_id: int,
    kp: str,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> KpAnalysisResponse:
    """某知识点题目集合的错误率与障碍分布。"""
    if not _teacher_teaches_class(db, teacher.id, class_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "无权查看该班级"},
        )

    rows = db.execute(
        select(StudentAnswer, Question)
        .join(Student, Student.id == StudentAnswer.student_id)
        .join(Question, Question.id == StudentAnswer.question_id)
        .where(Student.class_id == class_id, Student.deleted_at.is_(None))
    ).all()

    total = 0
    wrong = 0
    distribution = {k: 0 for k in BARRIER_KEYS}
    for answer, question in rows:
        if kp not in (question.knowledge_points or []):
            continue
        total += 1
        if not answer.is_correct:
            wrong += 1
            if answer.barrier_type is not None:
                distribution[answer.barrier_type.value] += 1

    error_rate = round(wrong / total, 2) if total else 0.0
    return KpAnalysisResponse(
        knowledge_point=kp,
        error_rate=error_rate,
        barrier_distribution=distribution,
    )


@router.get("/history/{student_id}", response_model=list[StudentHistoryOut], summary="学生诊断历史")
def student_history(
    student_id: int,
    teacher: Teacher = Depends(get_current_teacher),
    db: Session = Depends(get_db),
) -> list[StudentHistoryOut]:
    """按考试分组返回该生准确率与障碍分布趋势。"""
    student = db.execute(
        select(Student).where(
            Student.id == student_id, Student.deleted_at.is_(None)
        )
    ).scalar_one_or_none()
    if student is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "not_found", "message": "学生不存在"},
        )
    if not _teacher_teaches_class(db, teacher.id, student.class_id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail={"error": "forbidden", "message": "无权查看该学生"},
        )

    answers = db.execute(
        select(StudentAnswer)
        .where(StudentAnswer.student_id == student_id)
        .order_by(StudentAnswer.exam_id)
    ).scalars().all()

    by_exam: dict[int, list[StudentAnswer]] = {}
    for a in answers:
        by_exam.setdefault(a.exam_id, []).append(a)

    result: list[StudentHistoryOut] = []
    for exam_id in sorted(by_exam):
        items = by_exam[exam_id]
        correct = sum(1 for a in items if a.is_correct)
        accuracy = round(correct / len(items), 2) if items else 0.0
        distribution = {k: 0 for k in BARRIER_KEYS}
        for a in items:
            if not a.is_correct and a.barrier_type is not None:
                distribution[a.barrier_type.value] += 1
        result.append(
            StudentHistoryOut(
                exam_id=exam_id,
                accuracy=accuracy,
                barrier_distribution=distribution,
            )
        )
    return result
