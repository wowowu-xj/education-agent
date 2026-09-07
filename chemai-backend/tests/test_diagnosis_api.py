# -*- coding: utf-8 -*-
"""障碍诊断 API 集成测试（L2）。

经 TestClient + 真实 JWT 走完整链路；诊断引擎经 dependency_overrides
注入 FakeLLM，避免真实 DashScope 调用。覆盖 tasks §7：run-llm、barrier、
override、config、class/stats、class/kp、history 七端点与数据隔离。
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.api.diagnosis import get_diagnosis_engine
from app.api.learning_plan import get_plan_generator
from app.core.database import get_db
from app.core.enums import (
    ApprovalStatus,
    BarrierType,
    Difficulty,
    MisconceptionCategory,
    ParentRelation,
    QuestionType,
    TeacherRole,
)
from app.core.jwt import create_access_token
from app.main import create_app
from app.models import (
    Account,
    Class,
    DiagnosisOverrideLog,
    Exam,
    Grade,
    Paper,
    Parent,
    ParentNotification,
    Question,
    School,
    Student,
    StudentAnswer,
    StudentParentBinding,
    Teacher,
    TeacherClassSubject,
)
from chem_skills.chemistry_diagnosis.engine.diagnosis import DiagnosisEngine
from chem_skills.chemistry_diagnosis.engine.learning_plan import LearningPlanGenerator


# ---------------------------------------------------------------------------
# FakeLLM：固定返回合法诊断，避免真实网络调用。
# ---------------------------------------------------------------------------

_VALID_LLM = {
    "barrier_type": "concept",
    "misconception_category": "chemical_equilibrium",
    "confidence": 0.9,
    "reasoning": "学生对平衡移动原理理解不清",
    "suggestion": "重讲勒夏特列原理",
}

_PLAN_RESULT = {
    "title": "化学平衡补强计划",
    "goal": "掌握勒夏特列原理",
    "items": ["复习平衡常数", "练习移动方向判断"],
    "duration_days": 7,
}


class FakeLLM:
    """记录调用次数、固定返回 _VALID_LLM 的假 LLM。"""

    def __init__(self, result: dict | None = None) -> None:
        self._result = result or _VALID_LLM
        self.calls = 0

    def chat(self, messages: list[dict[str, str]]) -> dict:
        self.calls += 1
        return self._result


@pytest.fixture()
def fake_llm() -> FakeLLM:
    return FakeLLM()


@pytest.fixture()
def plan_fake_llm() -> FakeLLM:
    return FakeLLM(result=_PLAN_RESULT)


@pytest.fixture()
def client(engine: Engine, fake_llm: FakeLLM, plan_fake_llm: FakeLLM) -> TestClient:
    """带测试引擎的 FastAPI 应用，注入 FakeLLM 诊断引擎与计划生成器。"""
    app = create_app()
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    # 计划生成器带进程内缓存，跨请求必须共享同一实例，故此处用闭包持有单例。
    diagnosis_engine = DiagnosisEngine(fake_llm)
    plan_generator = LearningPlanGenerator(plan_fake_llm)

    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_diagnosis_engine] = lambda: diagnosis_engine
    app.dependency_overrides[get_plan_generator] = lambda: plan_generator
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def seeded(engine: Engine) -> dict:
    """种子：学校 + 教师 + 账号 + 班级 + 任课关系，返回 id。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    school = School(name="测试中学", region="北京市")
    s.add(school)
    s.flush()
    teacher = Teacher(
        name="张老师",
        phone="13800000001",
        school_id=school.id,
        role=TeacherRole.TEACHER,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    s.add(teacher)
    s.flush()
    account = Account(username="zhang", password_hash="x", teacher_id=teacher.id, role="teacher")
    s.add(account)
    s.flush()
    grade = Grade(name="高一", school_id=school.id)
    s.add(grade)
    s.flush()
    klass = Class(name="高一(1)班", grade_id=grade.id, subject="chemistry")
    s.add(klass)
    s.flush()
    # 任课关系：诊断查询/覆盖端点均要求教师任课该班。
    s.add(TeacherClassSubject(teacher_id=teacher.id, class_id=klass.id, subject="chemistry"))
    s.commit()
    ids = {
        "account_id": account.id,
        "teacher_id": teacher.id,
        "school_id": school.id,
        "class_id": klass.id,
    }
    s.close()
    return ids


@pytest.fixture()
def auth(seeded: dict) -> dict[str, str]:
    """主教师鉴权头。"""
    token = create_access_token(
        user_id=seeded["account_id"], role="teacher", school_id=seeded["school_id"]
    )
    return {"Authorization": f"Bearer {token}"}


@pytest.fixture()
def diag_seed(engine: Engine, seeded: dict) -> dict:
    """种子：学生 + 题目 + 试卷 + 考试，返回 id。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    student = Student(name="小明", class_id=seeded["class_id"], student_number="S001")
    s.add(student)
    s.flush()
    q = Question(
        content="下列关于化学平衡的说法正确的是？",
        type=QuestionType.SINGLE_CHOICE,
        options=["A", "B", "C", "D"],
        answer="A",
        analysis="勒夏特列原理",
        knowledge_points=["化学平衡"],
        difficulty=Difficulty.MEDIUM,
        score=2.0,
        teacher_id=seeded["teacher_id"],
    )
    s.add(q)
    s.flush()
    paper = Paper(title="诊断测试", teacher_id=seeded["teacher_id"], duration=60)
    s.add(paper)
    s.flush()
    exam = Exam(paper_id=paper.id, class_id=seeded["class_id"])
    s.add(exam)
    s.commit()
    ids = {
        "student_id": student.id,
        "question_id": q.id,
        "paper_id": paper.id,
        "exam_id": exam.id,
        "class_id": seeded["class_id"],
        "teacher_id": seeded["teacher_id"],
    }
    s.close()
    return ids


def _seed_other_teacher(engine: Engine, school_id: int) -> dict[str, str]:
    """在同校再种一位教师（不任课），返回其鉴权头。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    teacher = Teacher(
        name="李老师",
        phone="13800000002",
        school_id=school_id,
        role=TeacherRole.TEACHER,
        status=ApprovalStatus.APPROVED,
        subject="chemistry",
    )
    s.add(teacher)
    s.flush()
    account = Account(username="li", password_hash="x", teacher_id=teacher.id, role="teacher")
    s.add(account)
    s.commit()
    token = create_access_token(user_id=account.id, role="teacher", school_id=school_id)
    s.close()
    return {"Authorization": f"Bearer {token}"}


def _add_answer(
    engine: Engine,
    *,
    student_id: int,
    exam_id: int,
    question_id: int,
    text: str,
    is_correct: bool = False,
    barrier_type: BarrierType | None = None,
    misconception: MisconceptionCategory | None = None,
) -> int:
    """插入一条作答，返回其 id。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    a = StudentAnswer(
        student_id=student_id,
        exam_id=exam_id,
        question_id=question_id,
        is_correct=is_correct,
        student_answer=text,
        barrier_type=barrier_type,
        misconception_category=misconception,
    )
    s.add(a)
    s.commit()
    aid = a.id
    s.close()
    return aid


# ---------------------------------------------------------------------------
# 7.1 / 7.2 run-llm
# ---------------------------------------------------------------------------


class TestRunLLM:
    def test_run_llm_writes_back(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine,
            student_id=diag_seed["student_id"],
            exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"],
            text="我把平衡移动的方向判断错了",
        )
        resp = client.post(f"/api/diagnosis/run-llm/{diag_seed['exam_id']}", headers=auth)
        assert resp.status_code == 200
        data = resp.json()
        assert data["analyzed_count"] == 1
        assert data["failed_count"] == 0

        factory = sessionmaker(bind=engine, expire_on_commit=False)
        s = factory()
        a = s.execute(
            select(StudentAnswer).where(StudentAnswer.student_id == diag_seed["student_id"])
        ).scalar_one()
        assert a.barrier_type == BarrierType.CONCEPT
        assert a.misconception_category == MisconceptionCategory.CHEMICAL_EQUILIBRIUM
        assert a.confidence == 0.9

        # 双维度画像聚合写回 Student（design D6 / spec「学生画像聚合」）
        student = s.get(Student, diag_seed["student_id"])
        assert student.barrier_profile == {
            "concept": 1.0, "reading": 0.0, "expression": 0.0,
        }
        assert student.misconception_profile == {
            "chemical_equilibrium": 1.0,
            "redox": 0.0,
            "mole_calculation": 0.0,
            "organic_chemistry": 0.0,
            "chemical_notation": 0.0,
            "structure_properties": 0.0,
        }
        assert student.barrier_updated_at is not None
        s.close()

    def test_run_llm_skips_correct_and_diagnosed(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine
    ) -> None:
        # 正确作答 + 已诊断作答，均应被过滤，本次无可诊断对象
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="对", is_correct=True,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错",
            barrier_type=BarrierType.READING,
        )
        resp = client.post(f"/api/diagnosis/run-llm/{diag_seed['exam_id']}", headers=auth)
        assert resp.status_code == 200
        assert resp.json() == {"analyzed_count": 0, "failed_count": 0}

    def test_run_llm_other_teacher_404(self, client: TestClient, auth: dict, seeded: dict, diag_seed: dict, engine: Engine) -> None:
        other_auth = _seed_other_teacher(engine, seeded["school_id"])
        resp = client.post(f"/api/diagnosis/run-llm/{diag_seed['exam_id']}", headers=other_auth)
        assert resp.status_code == 404


# ---------------------------------------------------------------------------
# 7.3 / 7.4 barrier 班级障碍分布
# ---------------------------------------------------------------------------


class TestBarrierDistribution:
    def test_barrier_distribution(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="a",
            barrier_type=BarrierType.CONCEPT, misconception=MisconceptionCategory.CHEMICAL_EQUILIBRIUM,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="b",
            barrier_type=BarrierType.CONCEPT, misconception=MisconceptionCategory.CHEMICAL_EQUILIBRIUM,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="c",
            barrier_type=BarrierType.READING, misconception=MisconceptionCategory.REDOX,
        )
        resp = client.get(
            f"/api/diagnosis/barrier/{diag_seed['class_id']}/{diag_seed['exam_id']}", headers=auth
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["class_barrier_distribution"] == {"concept": 1, "reading": 0, "expression": 0}

        assert len(data["students"]) == 1
        student = data["students"][0]
        assert student["student_id"] == diag_seed["student_id"]
        assert student["student_name"] == "小明"
        assert student["dominant_barrier"] == "concept"
        # 迷思概念 → 知识点映射
        assert "化学平衡" in student["weak_knowledge_points"]
        assert "氧化还原反应" in student["weak_knowledge_points"]


# ---------------------------------------------------------------------------
# 7.5 / 7.6 override 教师覆盖
# ---------------------------------------------------------------------------


class TestOverride:
    def test_override_writes_profile_and_log(
        self, client: TestClient, auth: dict, seeded: dict, diag_seed: dict, engine: Engine
    ) -> None:
        resp = client.put(
            f"/api/diagnosis/override/{diag_seed['student_id']}",
            json={"barrier_type": "reading", "reason": "教师人工判断"},
            headers=auth,
        )
        assert resp.status_code == 200
        assert resp.json()["barrier_profile"] == {
            "concept": 0.05, "reading": 0.9, "expression": 0.05,
        }

        factory = sessionmaker(bind=engine, expire_on_commit=False)
        s = factory()
        logs = s.execute(
            select(DiagnosisOverrideLog).where(
                DiagnosisOverrideLog.student_id == diag_seed["student_id"]
            )
        ).scalars().all()
        assert len(logs) == 1
        assert logs[0].reason == "教师人工判断"
        assert logs[0].operator_id == seeded["teacher_id"]
        assert logs[0].new_profile == {"concept": 0.05, "reading": 0.9, "expression": 0.05}
        s.close()

    def test_override_invalid_type_422(self, client: TestClient, auth: dict, diag_seed: dict) -> None:
        resp = client.put(
            f"/api/diagnosis/override/{diag_seed['student_id']}",
            json={"barrier_type": "bogus", "reason": "x"},
            headers=auth,
        )
        assert resp.status_code == 422

    def test_override_other_teacher_403(
        self, client: TestClient, auth: dict, seeded: dict, diag_seed: dict, engine: Engine
    ) -> None:
        other_auth = _seed_other_teacher(engine, seeded["school_id"])
        resp = client.put(
            f"/api/diagnosis/override/{diag_seed['student_id']}",
            json={"barrier_type": "reading", "reason": "x"},
            headers=other_auth,
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7.7 / 7.8 config 阈值配置
# ---------------------------------------------------------------------------


class TestConfig:
    def test_config_defaults(self, client: TestClient, auth: dict, seeded: dict) -> None:
        resp = client.get(f"/api/diagnosis/config/{seeded['teacher_id']}", headers=auth)
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_threshold"] == 3
        assert data["reading_threshold"] == 2
        assert data["expression_threshold"] == 3
        assert data["mastery_threshold"] == 3
        assert data["auto_sync_to_student"] is False

    def test_config_upsert(self, client: TestClient, auth: dict, seeded: dict) -> None:
        resp = client.put(
            f"/api/diagnosis/config/{seeded['teacher_id']}",
            json={"concept_threshold": 5, "auto_sync_to_student": True},
            headers=auth,
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["concept_threshold"] == 5
        assert data["reading_threshold"] == 2  # 未覆盖字段保持默认
        assert data["auto_sync_to_student"] is True

        again = client.get(f"/api/diagnosis/config/{seeded['teacher_id']}", headers=auth).json()
        assert again["concept_threshold"] == 5
        assert again["auto_sync_to_student"] is True

    def test_config_other_teacher_403(
        self, client: TestClient, auth: dict, seeded: dict, engine: Engine
    ) -> None:
        other_auth = _seed_other_teacher(engine, seeded["school_id"])
        resp = client.get(f"/api/diagnosis/config/{seeded['teacher_id']}", headers=other_auth)
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 7.9 / 7.10 查询端点
# ---------------------------------------------------------------------------


class TestQueryEndpoints:
    def test_class_stats(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="a", barrier_type=BarrierType.CONCEPT,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="b", barrier_type=BarrierType.READING,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="对", is_correct=True,
        )
        resp = client.get(f"/api/diagnosis/class/{diag_seed['class_id']}/stats", headers=auth)
        assert resp.status_code == 200
        data = resp.json()
        assert data["student_count"] == 1
        assert data["answer_count"] == 2  # 正确作答不计入
        assert data["barrier_distribution"]["concept"] == 1
        assert data["barrier_distribution"]["reading"] == 1

    def test_kp_analysis(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="a", barrier_type=BarrierType.CONCEPT,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="对", is_correct=True,
        )
        resp = client.get(
            f"/api/diagnosis/class/{diag_seed['class_id']}/kp/化学平衡", headers=auth
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["knowledge_point"] == "化学平衡"
        assert data["error_rate"] == 0.5
        assert data["barrier_distribution"]["concept"] == 1

    def test_history(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="a", barrier_type=BarrierType.CONCEPT,
        )
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="对", is_correct=True,
        )
        resp = client.get(f"/api/diagnosis/history/{diag_seed['student_id']}", headers=auth)
        assert resp.status_code == 200
        data = resp.json()
        assert len(data) == 1
        assert data[0]["exam_id"] == diag_seed["exam_id"]
        assert data[0]["accuracy"] == 0.5
        assert data[0]["barrier_distribution"]["concept"] == 1


# ---------------------------------------------------------------------------
# §8 学习计划子系统
# ---------------------------------------------------------------------------


def _bind_parent(engine: Engine, student_id: int) -> int:
    """为学生绑定一位家长，返回 parent_id。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    parent = Parent(name="王妈妈", phone="13900000001", password_hash="x")
    s.add(parent)
    s.flush()
    s.add(
        StudentParentBinding(
            student_id=student_id,
            parent_id=parent.id,
            relationship_type=ParentRelation.MOTHER,
        )
    )
    s.commit()
    pid = parent.id
    s.close()
    return pid


def _read_current_plan(engine: Engine, student_id: int) -> dict | None:
    """读取学生 current_plan。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    plan = s.execute(
        select(Student.current_plan).where(Student.id == student_id)
    ).scalar()
    s.close()
    return plan


def _count_notifications(engine: Engine, student_id: int) -> list[ParentNotification]:
    """按学生取家长通知。"""
    factory = sessionmaker(bind=engine, expire_on_commit=False)
    s = factory()
    rows = s.execute(
        select(ParentNotification).where(ParentNotification.student_id == student_id)
    ).scalars().all()
    s.close()
    return rows


class TestLearningPlan:
    def test_generate_and_cache_hit(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine, plan_fake_llm: FakeLLM
    ) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错",
            barrier_type=BarrierType.CONCEPT, misconception=MisconceptionCategory.CHEMICAL_EQUILIBRIUM,
        )
        r1 = client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        assert r1.status_code == 200
        assert r1.json()["title"] == "化学平衡补强计划"

        r2 = client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        assert r2.status_code == 200
        assert r2.json() == r1.json()
        assert plan_fake_llm.calls == 1  # 24h 缓存命中，未二次调用 LLM

    def test_apply_writes_current_plan(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine
    ) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错", barrier_type=BarrierType.CONCEPT,
        )
        client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        resp = client.post(f"/api/learning-plans/{diag_seed['student_id']}/apply", headers=auth)
        assert resp.status_code == 200
        assert resp.json()["title"] == "化学平衡补强计划"
        assert _read_current_plan(engine, diag_seed["student_id"]) == _PLAN_RESULT

    def test_apply_without_generate_409(self, client: TestClient, auth: dict, diag_seed: dict) -> None:
        resp = client.post(f"/api/learning-plans/{diag_seed['student_id']}/apply", headers=auth)
        assert resp.status_code == 409

    def test_send_to_parent_writes_notification(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine
    ) -> None:
        parent_id = _bind_parent(engine, diag_seed["student_id"])
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错", barrier_type=BarrierType.CONCEPT,
        )
        client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        resp = client.post(
            f"/api/learning-plans/{diag_seed['student_id']}/send-to-parent", headers=auth
        )
        assert resp.status_code == 200
        data = resp.json()
        assert data["count"] == 1
        assert data["sent_to"] == [parent_id]

        rows = _count_notifications(engine, diag_seed["student_id"])
        assert len(rows) == 1
        assert rows[0].type == "learning_plan"
        assert "化学平衡补强计划" in rows[0].content

    def test_send_to_parent_no_bound_parent_400(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine
    ) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错", barrier_type=BarrierType.CONCEPT,
        )
        client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        resp = client.post(
            f"/api/learning-plans/{diag_seed['student_id']}/send-to-parent", headers=auth
        )
        assert resp.status_code == 400
        assert _count_notifications(engine, diag_seed["student_id"]) == []

    def test_get_plan_returns_generated(
        self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine
    ) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错", barrier_type=BarrierType.CONCEPT,
        )
        client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        resp = client.get(f"/api/learning-plans/{diag_seed['student_id']}", headers=auth)
        assert resp.status_code == 200
        assert resp.json()["title"] == "化学平衡补强计划"

    def test_delete_plan(self, client: TestClient, auth: dict, diag_seed: dict, engine: Engine) -> None:
        _add_answer(
            engine, student_id=diag_seed["student_id"], exam_id=diag_seed["exam_id"],
            question_id=diag_seed["question_id"], text="错", barrier_type=BarrierType.CONCEPT,
        )
        client.post(
            "/api/learning-plans/generate", json={"student_id": diag_seed["student_id"]}, headers=auth
        )
        resp = client.delete(f"/api/learning-plans/{diag_seed['student_id']}", headers=auth)
        assert resp.status_code == 204
        # 缓存已清且未应用 → get 404
        assert client.get(f"/api/learning-plans/{diag_seed['student_id']}", headers=auth).status_code == 404
