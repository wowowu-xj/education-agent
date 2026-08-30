# -*- coding: utf-8 -*-
"""题库/组卷/考试 API 集成测试（L2）+ 教师数据隔离测试。

经 TestClient + 真实 JWT 走完整链路：认证中间件 → 依赖注入 → 路由 → DB。
种子数据用独立会话（expire_on_commit=False + close）避免与请求会话争用
StaticPool 的单连接。
"""
from __future__ import annotations

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.engine import Engine
from sqlalchemy.orm import sessionmaker

from app.core.database import get_db
from app.core.enums import (
    ApprovalStatus,
    Difficulty,
    ExamStatus,
    PaperStatus,
    QuestionType,
    TeacherRole,
)
from app.core.jwt import create_access_token
from app.main import create_app
from app.models import (
    Account,
    Class,
    Exam,
    Grade,
    Paper,
    PaperQuestion,
    Question,
    QuestionSet,
    School,
    Teacher,
)


# ---------------------------------------------------------------------------
# fixtures
# ---------------------------------------------------------------------------


@pytest.fixture()
def client(engine: Engine) -> TestClient:
    """带测试引擎的 FastAPI 应用，get_db 每次请求给一个独立会话。"""
    app = create_app()
    factory = sessionmaker(bind=engine, expire_on_commit=False)

    def override_get_db():
        db = factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as c:
        yield c


@pytest.fixture()
def seeded(engine: Engine) -> dict:
    """种子：学校 + 教师 + 账号 + 班级，返回可用 id。"""
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


def _seed_other_teacher(engine: Engine, school_id: int) -> dict[str, str]:
    """在同校再种一位教师，返回其鉴权头。"""
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


# ---------------------------------------------------------------------------
# 工具
# ---------------------------------------------------------------------------


def _question_payload(**overrides) -> dict:
    payload = {
        "content": "下列反应中，属于氧化还原反应的是？",
        "type": "single_choice",
        "options": ["A", "B", "C", "D"],
        "answer": "C",
        "analysis": "有化合价变化",
        "knowledge_points": ["氧化还原反应"],
        "difficulty": "medium",
        "score": 2.0,
    }
    payload.update(overrides)
    return payload


def _create_question(client: TestClient, auth: dict, **overrides) -> dict:
    resp = client.post("/api/questions", json=_question_payload(**overrides), headers=auth)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _create_paper(client: TestClient, auth: dict, title: str = "期中测试") -> dict:
    resp = client.post("/api/papers", json={"title": title, "duration": 60}, headers=auth)
    assert resp.status_code == 201, resp.text
    return resp.json()


def _add_question_to_paper(client: TestClient, auth: dict, paper_id: int, question_id: int) -> None:
    resp = client.post(
        f"/api/papers/{paper_id}/questions",
        json={"question_id": question_id, "sort_order": 1},
        headers=auth,
    )
    assert resp.status_code == 201, resp.text


def _publish(client: TestClient, auth: dict, paper_id: int, class_ids: list[int]) -> dict:
    resp = client.post(
        f"/api/papers/{paper_id}/publish", json={"class_ids": class_ids}, headers=auth
    )
    assert resp.status_code == 200, resp.text
    return resp.json()


# ---------------------------------------------------------------------------
# 题库 CRUD（Section 2）
# ---------------------------------------------------------------------------


class TestQuestionCrud:
    def test_create_question(self, client: TestClient, auth: dict) -> None:
        data = _create_question(client, auth)
        assert data["type"] == "single_choice"
        assert data["difficulty"] == "medium"
        assert data["knowledge_points"] == ["氧化还原反应"]
        assert data["teacher_id"] is not None

    def test_create_question_rejects_invalid_type(self, client: TestClient, auth: dict) -> None:
        resp = client.post(
            "/api/questions", json=_question_payload(type="essay_plus"), headers=auth
        )
        assert resp.status_code == 422

    def test_list_questions_filters(self, client: TestClient, auth: dict) -> None:
        _create_question(client, auth)  # medium / 氧化还原反应
        _create_question(
            client,
            auth,
            content="摩尔计算题",
            type="calculation",
            knowledge_points=["摩尔计算"],
            difficulty="hard",
            region="全国",
            year=2024,
        )

        resp = client.get("/api/questions", headers=auth)
        assert resp.status_code == 200
        assert len(resp.json()) == 2

        # 按题型
        assert len(client.get("/api/questions?type=calculation", headers=auth).json()) == 1
        # 按难度
        assert len(client.get("/api/questions?difficulty=hard", headers=auth).json()) == 1
        # 按知识点
        assert (
            len(client.get("/api/questions?knowledge_point=摩尔计算", headers=auth).json()) == 1
        )
        # 按地区/年份
        assert len(client.get("/api/questions?region=全国&year=2024", headers=auth).json()) == 1

    def test_get_update_delete_question(self, client: TestClient, auth: dict) -> None:
        data = _create_question(client, auth)
        qid = data["id"]

        assert client.get(f"/api/questions/{qid}", headers=auth).status_code == 200

        resp = client.put(
            f"/api/questions/{qid}", json={"score": 5.0, "answer": "B"}, headers=auth
        )
        assert resp.status_code == 200
        assert resp.json()["score"] == 5.0
        assert resp.json()["answer"] == "B"

        assert client.delete(f"/api/questions/{qid}", headers=auth).status_code == 204
        assert client.get(f"/api/questions/{qid}", headers=auth).status_code == 404

    def test_delete_question_locked_paper_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        _publish(client, auth, paper["id"], [seeded["class_id"]])

        resp = client.delete(f"/api/questions/{q['id']}", headers=auth)
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# 题库文件夹（Section 2）
# ---------------------------------------------------------------------------


class TestQuestionSetCrud:
    def test_question_set_crud(self, client: TestClient, auth: dict) -> None:
        created = client.post(
            "/api/question-sets", json={"name": "氧化还原专题"}, headers=auth
        ).json()
        assert created["question_count"] == 0

        assert len(client.get("/api/question-sets", headers=auth).json()) == 1

        updated = client.put(
            f"/api/question-sets/{created['id']}", json={"name": "氧化还原进阶"}, headers=auth
        )
        assert updated.json()["name"] == "氧化还原进阶"

        assert client.delete(f"/api/question-sets/{created['id']}", headers=auth).status_code == 204
        assert len(client.get("/api/question-sets", headers=auth).json()) == 0

    def test_preset_set_not_deletable(
        self, client: TestClient, auth: dict, seeded: dict, engine: Engine
    ) -> None:
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        s = factory()
        preset = QuestionSet(name="我的预设", teacher_id=seeded["teacher_id"], is_preset=True)
        s.add(preset)
        s.commit()
        preset_id = preset.id
        s.close()

        resp = client.delete(f"/api/question-sets/{preset_id}", headers=auth)
        assert resp.status_code == 409

    def test_add_remove_question_in_set(self, client: TestClient, auth: dict) -> None:
        q = _create_question(client, auth)
        set_obj = client.post(
            "/api/question-sets", json={"name": "专题"}, headers=auth
        ).json()

        # 加题
        resp = client.post(
            f"/api/question-sets/{set_obj['id']}/questions",
            json={"question_id": q["id"], "sort_order": 0},
            headers=auth,
        )
        assert resp.status_code == 201

        # 重复加题 409
        resp = client.post(
            f"/api/question-sets/{set_obj['id']}/questions", json={"question_id": q["id"]}, headers=auth
        )
        assert resp.status_code == 409

        # 计数派生
        detail = client.get(f"/api/question-sets/{set_obj['id']}", headers=auth).json()
        assert detail["question_count"] == 1

        # 移题（不删题）
        resp = client.delete(
            f"/api/question-sets/{set_obj['id']}/questions/{q['id']}", headers=auth
        )
        assert resp.status_code == 204
        assert client.get(f"/api/questions/{q['id']}", headers=auth).status_code == 200

    def test_question_set_count_excludes_soft_deleted_question(
        self, client: TestClient, auth: dict
    ) -> None:
        q1 = _create_question(client, auth)
        q2 = _create_question(client, auth, content="第二题", type="true_false")
        set_obj = client.post("/api/question-sets", json={"name": "专题"}, headers=auth).json()

        client.post(
            f"/api/question-sets/{set_obj['id']}/questions",
            json={"question_id": q1["id"]},
            headers=auth,
        )
        client.post(
            f"/api/question-sets/{set_obj['id']}/questions",
            json={"question_id": q2["id"]},
            headers=auth,
        )

        # 软删其中一题（文件夹引用不拦截删除）
        assert client.delete(f"/api/questions/{q2['id']}", headers=auth).status_code == 204

        # 详情（helper）与列表（批量）计数均排除软删题
        detail = client.get(f"/api/question-sets/{set_obj['id']}", headers=auth).json()
        assert detail["question_count"] == 1
        listed = client.get("/api/question-sets", headers=auth).json()
        assert listed[0]["question_count"] == 1


# ---------------------------------------------------------------------------
# 组卷与发布（Section 3）
# ---------------------------------------------------------------------------


class TestPaperAndPublish:
    def test_create_paper_defaults_draft(self, client: TestClient, auth: dict) -> None:
        paper = _create_paper(client, auth)
        assert paper["status"] == "draft"
        assert paper["question_count"] == 0
        assert paper["total_score"] == 0.0

    def test_update_locked_paper_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        _publish(client, auth, paper["id"], [seeded["class_id"]])

        resp = client.put(f"/api/papers/{paper['id']}", json={"title": "改名"}, headers=auth)
        assert resp.status_code == 409

    def test_add_question_locked_paper_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q1 = _create_question(client, auth)
        q2 = _create_question(client, auth, content="第二题", type="true_false")
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])
        _publish(client, auth, paper["id"], [seeded["class_id"]])

        resp = client.post(
            f"/api/papers/{paper['id']}/questions", json={"question_id": q2["id"]}, headers=auth
        )
        assert resp.status_code == 409

    def test_publish_creates_exam_per_class(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])

        result = _publish(client, auth, paper["id"], [seeded["class_id"]])
        assert result["status"] == "locked"
        assert len(result["exam_ids"]) == 1

        # 试卷详情派生 total_score / question_count
        detail = client.get(f"/api/papers/{paper['id']}", headers=auth).json()
        assert detail["question_count"] == 1
        assert detail["total_score"] == 2.0

    def test_paper_derived_excludes_soft_deleted_question(
        self, client: TestClient, auth: dict
    ) -> None:
        q1 = _create_question(client, auth)  # score 2.0
        q2 = _create_question(client, auth, content="第二题", type="true_false", score=3.0)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])
        _add_question_to_paper(client, auth, paper["id"], q2["id"])

        # 软删其中一题（draft 试卷引用不拦截删除）
        assert client.delete(f"/api/questions/{q2['id']}", headers=auth).status_code == 204

        detail = client.get(f"/api/papers/{paper['id']}", headers=auth).json()
        assert detail["question_count"] == 1
        assert detail["total_score"] == 2.0

    def test_publish_empty_paper_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        paper = _create_paper(client, auth)
        resp = client.post(
            f"/api/papers/{paper['id']}/publish", json={"class_ids": [seeded["class_id"]]}, headers=auth
        )
        assert resp.status_code == 409

    def test_publish_twice_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        _publish(client, auth, paper["id"], [seeded["class_id"]])

        resp = client.post(
            f"/api/papers/{paper['id']}/publish", json={"class_ids": [seeded["class_id"]]}, headers=auth
        )
        assert resp.status_code == 409

    def test_delete_paper_with_exam_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        _publish(client, auth, paper["id"], [seeded["class_id"]])

        resp = client.delete(f"/api/papers/{paper['id']}", headers=auth)
        assert resp.status_code == 409


# ---------------------------------------------------------------------------
# 考试状态机（Section 4）
# ---------------------------------------------------------------------------


class TestExamStateMachine:
    def _publish_and_get_exam(self, client: TestClient, auth: dict, seeded: dict) -> int:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        return _publish(client, auth, paper["id"], [seeded["class_id"]])["exam_ids"][0]

    def test_exam_list_filter(self, client: TestClient, auth: dict, seeded: dict) -> None:
        exam_id = self._publish_and_get_exam(client, auth, seeded)
        assert len(client.get("/api/exams", headers=auth).json()) == 1
        assert (
            len(
                client.get(
                    f"/api/exams?class_id={seeded['class_id']}", headers=auth
                ).json()
            )
            == 1
        )
        assert len(client.get("/api/exams?status_filter=published", headers=auth).json()) == 1
        assert len(client.get("/api/exams?status_filter=cancelled", headers=auth).json()) == 0

    def test_cancel_published_exam(self, client: TestClient, auth: dict, seeded: dict) -> None:
        exam_id = self._publish_and_get_exam(client, auth, seeded)
        resp = client.post(f"/api/exams/{exam_id}/cancel", headers=auth)
        assert resp.status_code == 200
        assert resp.json()["status"] == "cancelled"

    def test_cancel_cancelled_exam_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        exam_id = self._publish_and_get_exam(client, auth, seeded)
        client.post(f"/api/exams/{exam_id}/cancel", headers=auth)
        resp = client.post(f"/api/exams/{exam_id}/cancel", headers=auth)
        assert resp.status_code == 409

    def test_finalize_published_exam_409(self, client: TestClient, auth: dict, seeded: dict) -> None:
        exam_id = self._publish_and_get_exam(client, auth, seeded)
        resp = client.post(f"/api/exams/{exam_id}/finalize", headers=auth)
        assert resp.status_code == 409

    def test_finalize_grading_exam(self, client: TestClient, auth: dict, seeded: dict, engine: Engine) -> None:
        exam_id = self._publish_and_get_exam(client, auth, seeded)
        # 手动把状态推到 grading（学生作答链路的触发点本期 defer）
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        s = factory()
        exam = s.get(Exam, exam_id)
        exam.status = ExamStatus.GRADING
        s.commit()
        s.close()

        resp = client.post(f"/api/exams/{exam_id}/finalize", headers=auth)
        assert resp.status_code == 200
        assert resp.json()["status"] == "completed"


# ---------------------------------------------------------------------------
# 数据隔离（Section 7.3）
# ---------------------------------------------------------------------------


class TestDataIsolation:
    def test_cannot_access_others_question(self, client: TestClient, auth: dict, seeded: dict, engine: Engine) -> None:
        q = _create_question(client, auth)
        other_auth = _seed_other_teacher(engine, seeded["school_id"])

        # 他人题目不可见（列表为空、详情 404）
        assert len(client.get("/api/questions", headers=other_auth).json()) == 0
        assert client.get(f"/api/questions/{q['id']}", headers=other_auth).status_code == 404
        # 删除也 404（被 teacher_id 过滤，视为不存在）
        assert client.delete(f"/api/questions/{q['id']}", headers=other_auth).status_code == 404

    def test_cannot_access_others_paper(self, client: TestClient, auth: dict, seeded: dict, engine: Engine) -> None:
        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])
        other_auth = _seed_other_teacher(engine, seeded["school_id"])

        assert len(client.get("/api/papers", headers=other_auth).json()) == 0
        assert client.get(f"/api/papers/{paper['id']}", headers=other_auth).status_code == 404

    def test_cannot_publish_to_other_school_class(
        self, client: TestClient, auth: dict, seeded: dict, engine: Engine
    ) -> None:
        # 另建一所学校及其班级
        factory = sessionmaker(bind=engine, expire_on_commit=False)
        s = factory()
        other_school = School(name="别的学校")
        s.add(other_school)
        s.flush()
        other_grade = Grade(name="高一", school_id=other_school.id)
        s.add(other_grade)
        s.flush()
        other_class = Class(name="别校班级", grade_id=other_grade.id, subject="chemistry")
        s.add(other_class)
        s.commit()
        other_class_id = other_class.id
        s.close()

        q = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q["id"])

        resp = client.post(
            f"/api/papers/{paper['id']}/publish", json={"class_ids": [other_class_id]}, headers=auth
        )
        assert resp.status_code == 403


# ---------------------------------------------------------------------------
# 试卷导出（Section 6）
# ---------------------------------------------------------------------------


class TestPaperExport:
    def test_export_html_sorted_by_sort_order(self, client: TestClient, auth: dict) -> None:
        q1 = _create_question(client, auth)  # 默认 content 含「氧化还原」
        q2 = _create_question(client, auth, content="第二题", type="true_false")
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])  # sort_order=1
        client.post(
            f"/api/papers/{paper['id']}/questions",
            json={"question_id": q2["id"], "sort_order": 0},
            headers=auth,
        )

        resp = client.get(f"/api/papers/{paper['id']}/export?format=html", headers=auth)
        assert resp.status_code == 200
        assert "期中测试" in resp.text
        assert "总分" in resp.text
        # sort_order=0 的 q2 排在 q1 之前
        assert resp.text.index("第二题") < resp.text.index("氧化还原")

    def test_export_html_without_answer(self, client: TestClient, auth: dict) -> None:
        q1 = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])

        resp = client.get(
            f"/api/papers/{paper['id']}/export?format=html&include_answer=false", headers=auth
        )
        assert resp.status_code == 200
        assert "答案" not in resp.text
        assert "解析" not in resp.text

    def test_export_docx(self, client: TestClient, auth: dict) -> None:
        q1 = _create_question(client, auth)
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])

        resp = client.get(f"/api/papers/{paper['id']}/export?format=docx", headers=auth)
        assert resp.status_code == 200
        assert resp.headers["content-type"].startswith(
            "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
        )

    def test_export_draft_paper_allowed(self, client: TestClient, auth: dict) -> None:
        # 未发布的 draft 试卷也允许导出（预览用途）
        paper = _create_paper(client, auth)
        resp = client.get(f"/api/papers/{paper['id']}/export?format=html", headers=auth)
        assert resp.status_code == 200

    def test_export_other_teachers_paper_404(self, client: TestClient, auth: dict, seeded: dict, engine: Engine) -> None:
        paper = _create_paper(client, auth)
        other_auth = _seed_other_teacher(engine, seeded["school_id"])
        resp = client.get(f"/api/papers/{paper['id']}/export?format=html", headers=other_auth)
        assert resp.status_code == 404

    def test_export_excludes_soft_deleted_question(self, client: TestClient, auth: dict) -> None:
        q1 = _create_question(client, auth)  # content 含「氧化还原」
        q2 = _create_question(client, auth, content="第二题", type="true_false")
        paper = _create_paper(client, auth)
        _add_question_to_paper(client, auth, paper["id"], q1["id"])
        _add_question_to_paper(client, auth, paper["id"], q2["id"])

        # 软删其中一题（draft 试卷引用不拦截删除）
        assert client.delete(f"/api/questions/{q2['id']}", headers=auth).status_code == 204

        resp = client.get(f"/api/papers/{paper['id']}/export?format=html", headers=auth)
        assert resp.status_code == 200
        assert "第二题" not in resp.text
        assert "氧化还原" in resp.text
