# -*- coding: utf-8 -*-
"""数据完整性测试：锁住代码审查中修掉的每一条约束。

这个文件的每个用例都对应一条曾经**能写进库**的脏数据。删掉对应的约束，
这里必然有测试变红——这是防回退的护栏，不是覆盖率填充。

覆盖范围：
- 一人一账号（accounts.teacher_id / student_id 唯一）
- 外键 RESTRICT 真的拦住删除（而不是被 ORM 改写成 NULL 后撞 NOT NULL）
- 关系表不允许重复行（任课关系、亲子绑定）
- 枚举列的 CHECK 约束拦住绕过 ORM 的垃圾值
- 枚举按值（小写下划线）入库，不是按成员名
- 时间列读回来一定带 UTC 时区
- Teacher.role 变更自动同步到 Account.role
"""
from __future__ import annotations

from datetime import datetime, timedelta, timezone

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import DatabaseError, IntegrityError
from sqlalchemy.orm import Session

from app.core.enums import ApprovalStatus, ParentRelation, SchoolStage, TeacherRole
from app.core.security import hash_password
from app.models import (
    Account,
    Class,
    Grade,
    Parent,
    School,
    Student,
    StudentParentBinding,
    Teacher,
    TeacherClassSubject,
)

# --------------------------------------------------------------------------- #
# fixtures
# --------------------------------------------------------------------------- #


@pytest.fixture()
def student(db: Session, klass: Class) -> Student:
    """一名在读学生。"""
    obj = Student(name="王同学", student_number="2025990001", class_id=klass.id)
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def parent(db: Session) -> Parent:
    """一位家长。"""
    obj = Parent(name="王妈妈", phone="13911110001", password_hash=hash_password("Pa@ss1234"))
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


@pytest.fixture()
def teacher_account(db: Session, teacher: Teacher) -> Account:
    """教师张老师的登录账号。"""
    obj = Account(
        username="zhang",
        password_hash=hash_password("Te@cher1234"),
        teacher_id=teacher.id,
        role=teacher.role.value,
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj


# --------------------------------------------------------------------------- #
# P1-3 一人一账号
# --------------------------------------------------------------------------- #


class TestOnePersonOneAccount:
    """accounts.teacher_id / student_id 上的唯一约束。

    没有这两个唯一约束时，同一个人可以有多条 Account 记录。
    ``uselist=False`` 只是 ORM 侧的期望，加载关系时只会拿到一条 SAWarning
    和其中任意一条记录——登录密码校验会变成随机通过。
    """

    def test_teacher_cannot_have_two_accounts(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        db.add(
            Account(
                username="zhang_alt",
                password_hash=hash_password("Other@1234"),
                teacher_id=teacher.id,
                role=TeacherRole.TEACHER.value,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_student_cannot_have_two_accounts(self, db: Session, student: Student) -> None:
        db.add(
            Account(
                username="wang",
                password_hash=hash_password("Stu@1234"),
                student_id=student.id,
                role="student",
            )
        )
        db.commit()

        db.add(
            Account(
                username="wang_alt",
                password_hash=hash_password("Stu@1234"),
                student_id=student.id,
                role="student",
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_multiple_student_accounts_leave_teacher_id_null(
        self, db: Session, klass: Class
    ) -> None:
        """可空列的唯一约束允许多个 NULL——学生账号不会互相挤掉。"""
        students = [Student(name=f"学生{i}", class_id=klass.id) for i in range(3)]
        db.add_all(students)
        db.flush()

        db.add_all(
            [
                Account(
                    username=f"stu{i}",
                    password_hash=hash_password("Stu@1234"),
                    student_id=s.id,
                    role="student",
                )
                for i, s in enumerate(students)
            ]
        )
        db.commit()

        assert db.query(Account).filter(Account.teacher_id.is_(None)).count() == 3


# --------------------------------------------------------------------------- #
# P1-4 外键 RESTRICT
# --------------------------------------------------------------------------- #


class TestForeignKeyRestrict:
    """删除带下游数据的组织节点必须被数据库拦住。

    关键在 ``passive_deletes="all"``：没有它，ORM 会在 DELETE 前先把子行的
    外键 UPDATE 成 NULL。那些列是 NOT NULL，于是报错信息变成
    "NOT NULL constraint failed"——看起来像模型写错了，实际是 RESTRICT
    被 ORM 改写掉了，排查方向完全跑偏。
    """

    def test_cannot_delete_class_with_students(
        self, db: Session, klass: Class, student: Student
    ) -> None:
        db.delete(klass)
        with pytest.raises(DatabaseError) as exc_info:
            db.commit()
        db.rollback()

        # 必须是外键报错，不能是 NOT NULL——后者说明 ORM 抢先置空了 class_id
        assert "FOREIGN KEY" in str(exc_info.value).upper()
        assert db.get(Student, student.id) is not None

    def test_cannot_delete_school_with_teachers(
        self, db: Session, school: School, teacher: Teacher
    ) -> None:
        db.delete(school)
        with pytest.raises(DatabaseError) as exc_info:
            db.commit()
        db.rollback()

        assert "FOREIGN KEY" in str(exc_info.value).upper()
        assert db.get(Teacher, teacher.id) is not None

    def test_empty_school_can_be_deleted(self, db: Session) -> None:
        """反向确认：RESTRICT 不是无脑禁止删除。"""
        empty = School(name="空学校", region="测试区", current_semester="2025-秋")
        db.add(empty)
        db.commit()
        school_id = empty.id

        db.delete(empty)
        db.commit()

        assert db.get(School, school_id) is None

    def test_deleting_teacher_cascades_account(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        """删教师连带删账号，且不会撞 XOR CHECK。

        Teacher.account 上的 ``cascade + passive_deletes`` 就是为这条路径准备的：
        少了它，ORM 会把 accounts.teacher_id 置空，直接违反
        ``ck_accounts_teacher_xor_student``。
        """
        account_id = teacher_account.id

        db.delete(teacher)
        db.commit()

        assert db.get(Account, account_id) is None

    def test_deleting_school_cascades_grades_and_classes(self, db: Session) -> None:
        """学校 → 年级 → 班级 是 CASCADE 链（无学生时可一路删除）。"""
        school = School(name="待撤并中学", region="测试区", current_semester="2025-秋")
        db.add(school)
        db.flush()
        grade = Grade(name="初一", school_id=school.id, academic_year="2025-2026")
        db.add(grade)
        db.flush()
        klass = Class(name="初一（1）班", grade_id=grade.id, subject="chemistry")
        db.add(klass)
        db.commit()
        grade_id, class_id = grade.id, klass.id

        db.delete(school)
        db.commit()

        assert db.get(Grade, grade_id) is None
        assert db.get(Class, class_id) is None


# --------------------------------------------------------------------------- #
# P1-5 关系表唯一性
# --------------------------------------------------------------------------- #


class TestRelationTableUniqueness:
    """多对多关系表不允许重复行。

    重复行不会报错，只会让「按班级统计任课教师」「家长绑定列表」出现重影，
    而且删除时只删掉一条，剩下的继续污染统计。
    """

    def test_teacher_class_subject_is_unique(
        self, db: Session, teacher: Teacher, klass: Class
    ) -> None:
        db.add(
            TeacherClassSubject(teacher_id=teacher.id, class_id=klass.id, subject="chemistry")
        )
        db.commit()

        db.add(
            TeacherClassSubject(teacher_id=teacher.id, class_id=klass.id, subject="chemistry")
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_same_teacher_different_subject_is_allowed(
        self, db: Session, teacher: Teacher, klass: Class
    ) -> None:
        """唯一约束含 subject：同一教师在同一班级教两门课是合法的。"""
        db.add_all(
            [
                TeacherClassSubject(
                    teacher_id=teacher.id, class_id=klass.id, subject="chemistry"
                ),
                TeacherClassSubject(teacher_id=teacher.id, class_id=klass.id, subject="physics"),
            ]
        )
        db.commit()

        assert db.query(TeacherClassSubject).count() == 2

    def test_student_parent_binding_is_unique(
        self, db: Session, student: Student, parent: Parent
    ) -> None:
        db.add(
            StudentParentBinding(
                student_id=student.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.MOTHER,
            )
        )
        db.commit()

        db.add(
            StudentParentBinding(
                student_id=student.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.MOTHER,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()

    def test_binding_uniqueness_ignores_relationship_type(
        self, db: Session, student: Student, parent: Parent
    ) -> None:
        """换个 relationship_type 也不能新增第二条——同一个人不会既是母亲又是监护人。"""
        db.add(
            StudentParentBinding(
                student_id=student.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.MOTHER,
            )
        )
        db.commit()

        db.add(
            StudentParentBinding(
                student_id=student.id,
                parent_id=parent.id,
                relationship_type=ParentRelation.GUARDIAN,
            )
        )
        with pytest.raises(IntegrityError):
            db.commit()
        db.rollback()


# --------------------------------------------------------------------------- #
# P1-7 枚举 CHECK 约束
# --------------------------------------------------------------------------- #


def _expect_check_violation(db: Session, sql: str, params: dict[str, object]) -> None:
    """执行一条应该被 CHECK 约束拦住的原生 SQL。"""
    with pytest.raises(IntegrityError):
        db.execute(text(sql), params)
        db.commit()
    db.rollback()


class TestEnumCheckConstraints:
    """枚举列必须有数据库级 CHECK 约束。

    ``native_enum=False`` 且不带 ``create_constraint=True`` 时，枚举列在 MySQL /
    SQLite 上退化成普通 VARCHAR：ORM 之外的任何写入路径（迁移脚本、运维手改、
    批量导入、其他语言的服务）都能写进任意字符串，读回来时 ORM 抛
    ``LookupError``，而且是在毫不相关的查询里炸。
    """

    def test_teacher_role_rejects_garbage(self, db: Session, teacher: Teacher) -> None:
        _expect_check_violation(
            db, "UPDATE teachers SET role = :v WHERE id = :i", {"v": "super_god", "i": teacher.id}
        )

    def test_teacher_status_rejects_garbage(self, db: Session, teacher: Teacher) -> None:
        _expect_check_violation(
            db, "UPDATE teachers SET status = :v WHERE id = :i", {"v": "maybe", "i": teacher.id}
        )

    def test_student_status_rejects_garbage(self, db: Session, student: Student) -> None:
        _expect_check_violation(
            db, "UPDATE students SET status = :v WHERE id = :i", {"v": "unknown", "i": student.id}
        )

    def test_class_stage_rejects_garbage(self, db: Session, klass: Class) -> None:
        _expect_check_violation(
            db, "UPDATE classes SET stage = :v WHERE id = :i", {"v": "college", "i": klass.id}
        )

    def test_binding_relationship_rejects_garbage(
        self, db: Session, student: Student, parent: Parent
    ) -> None:
        binding = StudentParentBinding(
            student_id=student.id,
            parent_id=parent.id,
            relationship_type=ParentRelation.FATHER,
        )
        db.add(binding)
        db.commit()

        _expect_check_violation(
            db,
            "UPDATE student_parent_bindings SET relationship_type = :v WHERE id = :i",
            {"v": "隔壁老王", "i": binding.id},
        )

    def test_account_role_rejects_unknown_role(
        self, db: Session, teacher_account: Account
    ) -> None:
        """Account.role 是裸 String，靠显式 CHECK 约束守取值域。"""
        _expect_check_violation(
            db,
            "UPDATE accounts SET role = :v WHERE id = :i",
            {"v": "principal", "i": teacher_account.id},
        )

    def test_account_role_rejects_parent(self, db: Session, teacher_account: Account) -> None:
        """家长不进 Account 表（决策 #1），'parent' 不在取值域内。"""
        _expect_check_violation(
            db,
            "UPDATE accounts SET role = :v WHERE id = :i",
            {"v": "parent", "i": teacher_account.id},
        )

    def test_account_requires_exactly_one_owner(
        self, db: Session, teacher: Teacher, student: Student
    ) -> None:
        """XOR CHECK：teacher_id 和 student_id 不能同时有值，也不能同时为空。"""
        _expect_check_violation(
            db,
            "INSERT INTO accounts (username, password_hash, teacher_id, student_id, role)"
            " VALUES (:u, :p, :t, :s, :r)",
            {
                "u": "both",
                "p": "x",
                "t": teacher.id,
                "s": student.id,
                "r": TeacherRole.TEACHER.value,
            },
        )

        _expect_check_violation(
            db,
            "INSERT INTO accounts (username, password_hash, teacher_id, student_id, role)"
            " VALUES (:u, :p, NULL, NULL, :r)",
            {"u": "orphan", "p": "x", "r": TeacherRole.TEACHER.value},
        )


# --------------------------------------------------------------------------- #
# 枚举入库格式
# --------------------------------------------------------------------------- #


class TestEnumStorageFormat:
    """枚举必须按 ``.value``（小写下划线）入库，不能按成员名。

    SQLAlchemy 的 ``Enum`` 默认存成员**名**（``ACADEMIC_ADMIN``）。
    枚举定义的注释、API 契约、前端断言全部用的是值（``academic_admin``），
    默认行为会让库里的数据跟契约对不上，跨语言读库时直接踩坑。
    """

    def test_teacher_role_stored_as_value(self, db: Session, school: School) -> None:
        obj = Teacher(
            name="李教务",
            phone="13800000099",
            school_id=school.id,
            role=TeacherRole.ACADEMIC_ADMIN,
            status=ApprovalStatus.APPROVED,
            subject="chemistry",
        )
        db.add(obj)
        db.commit()

        raw = db.execute(
            text("SELECT role, status FROM teachers WHERE id = :i"), {"i": obj.id}
        ).one()
        assert raw.role == "academic_admin"
        assert raw.status == "approved"

    def test_class_stage_stored_as_value(self, db: Session, klass: Class) -> None:
        klass.stage = SchoolStage.SENIOR
        db.commit()

        raw = db.execute(text("SELECT stage FROM classes WHERE id = :i"), {"i": klass.id}).one()
        assert raw.stage == "senior"

    def test_enum_round_trips_to_member(self, db: Session, school: School) -> None:
        """读回来是枚举成员，不是字符串——服务层可以直接比较。"""
        obj = Teacher(
            name="赵组长",
            phone="13800000098",
            school_id=school.id,
            role=TeacherRole.SUBJECT_LEAD,
            status=ApprovalStatus.PENDING,
            subject="chemistry",
        )
        db.add(obj)
        db.commit()
        teacher_id = obj.id  # expunge 之前保存，否则访问 .id 触发 DetachedInstanceError
        db.expunge_all()

        loaded = db.get(Teacher, teacher_id)
        assert loaded is not None
        assert loaded.role is TeacherRole.SUBJECT_LEAD
        assert loaded.status is ApprovalStatus.PENDING


# --------------------------------------------------------------------------- #
# UTCDateTime
# --------------------------------------------------------------------------- #


class TestUTCDateTime:
    """时间列读回来一定带 UTC 时区。

    SQLite 和 MySQL 都不保存时区偏移，``DateTime(timezone=True)`` 只是个声明。
    直接用会读回 naive datetime，跟 aware datetime 做减法抛 TypeError——
    而且是在「计算 token 是否过期」这种关键路径上抛。
    """

    def test_timestamps_are_timezone_aware(self, teacher: Teacher) -> None:
        assert teacher.created_at.tzinfo is not None
        assert teacher.created_at.utcoffset() == timedelta(0)
        assert teacher.updated_at.tzinfo is not None

    def test_timestamps_support_arithmetic_with_aware_now(self, teacher: Teacher) -> None:
        """能直接和 aware now 做减法——这是当初 naive 时间踩的坑。"""
        age = datetime.now(tz=timezone.utc) - teacher.created_at
        assert age >= timedelta(0)

    def test_naive_input_is_treated_as_utc(self, db: Session, student: Student) -> None:
        student.last_practice_at = datetime(2026, 8, 4, 12, 0, 0)  # naive
        student_id = student.id
        db.commit()
        db.expunge_all()

        loaded = db.get(Student, student_id)
        assert loaded is not None
        assert loaded.last_practice_at == datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)

    def test_non_utc_input_is_normalized(self, db: Session, student: Student) -> None:
        """写入东八区时间，读回来是等价的 UTC 时刻。"""
        beijing = timezone(timedelta(hours=8))
        student.last_practice_at = datetime(2026, 8, 4, 20, 0, 0, tzinfo=beijing)
        student_id = student.id
        db.commit()
        db.expunge_all()

        loaded = db.get(Student, student_id)
        assert loaded is not None
        assert loaded.last_practice_at == datetime(2026, 8, 4, 12, 0, 0, tzinfo=timezone.utc)
        assert loaded.last_practice_at.utcoffset() == timedelta(0)


# --------------------------------------------------------------------------- #
# P1-8 角色同步
# --------------------------------------------------------------------------- #


class TestRoleSync:
    """Teacher.role 变更必须同步到 Account.role。

    Account.role 是为了避免登录时 JOIN 教师表而缓存的冗余列。签发 JWT 时读的是
    这一列，所以它一旦落后于 Teacher.role，教务把老师提为学科组长后，老师重新
    登录拿到的还是旧权限——而且数据库里看起来完全正常。
    """

    def test_promotion_syncs_account_role(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        assert teacher_account.role == TeacherRole.TEACHER.value

        teacher.role = TeacherRole.SUBJECT_LEAD
        account_id = teacher_account.id
        db.commit()
        db.expunge_all()

        loaded = db.get(Account, account_id)
        assert loaded is not None
        assert loaded.role == TeacherRole.SUBJECT_LEAD.value

    def test_demotion_syncs_account_role(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        account_id = teacher_account.id
        teacher.role = TeacherRole.ACADEMIC_ADMIN
        db.commit()
        teacher.role = TeacherRole.TEACHER
        db.commit()
        db.expunge_all()

        loaded = db.get(Account, account_id)
        assert loaded is not None
        assert loaded.role == TeacherRole.TEACHER.value

    def test_other_field_change_does_not_touch_role(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        """只在 role 真的变了的时候同步，改名字不触发。"""
        account_id = teacher_account.id
        teacher.name = "张老师（已改名）"
        db.commit()
        db.expunge_all()

        loaded = db.get(Account, account_id)
        assert loaded is not None
        assert loaded.role == TeacherRole.TEACHER.value

    def test_teacher_without_account_does_not_break(self, db: Session, teacher: Teacher) -> None:
        """没有账号的教师（未激活）改角色不应该报错。"""
        teacher.role = TeacherRole.ADMIN
        db.commit()

        assert teacher.account is None
        assert teacher.role is TeacherRole.ADMIN

    def test_synced_role_passes_check_constraint(
        self, db: Session, teacher: Teacher, teacher_account: Account
    ) -> None:
        """同步写入的是 ``.value``，能过 ck_accounts_role_allowed。"""
        for role in TeacherRole:
            teacher.role = role
            db.commit()
            db.refresh(teacher_account)
            assert teacher_account.role == role.value


# --------------------------------------------------------------------------- #
# 软删除
# --------------------------------------------------------------------------- #


class TestSoftDelete:
    """``SoftDeleteMixin`` 的辅助方法。"""

    def test_soft_delete_sets_deleted_at(self, db: Session, teacher: Teacher) -> None:
        assert teacher.is_deleted is False

        teacher.soft_delete()
        db.commit()

        assert teacher.is_deleted is True
        assert teacher.deleted_at is not None
        assert teacher.deleted_at.tzinfo is not None
        assert db.get(Teacher, teacher.id) is not None  # 行还在

    def test_soft_delete_is_idempotent(self, db: Session, teacher: Teacher) -> None:
        """重复调用不刷新时间戳——首次删除时间是审计依据。"""
        teacher.soft_delete()
        db.commit()
        first = teacher.deleted_at

        teacher.soft_delete()
        db.commit()

        assert teacher.deleted_at == first

    def test_soft_delete_accepts_explicit_time(self, db: Session, parent: Parent) -> None:
        moment = datetime(2026, 1, 1, tzinfo=timezone.utc)
        parent.soft_delete(at=moment)
        db.commit()

        assert parent.deleted_at == moment

    def test_parent_supports_soft_delete(self, parent: Parent) -> None:
        """Parent 之前漏了 SoftDeleteMixin，注销家长只能物理删除。"""
        assert hasattr(parent, "deleted_at")
        assert parent.is_deleted is False


# --------------------------------------------------------------------------- #
# 约束命名
# --------------------------------------------------------------------------- #


class TestConstraintNaming:
    """约束必须有稳定的、可预测的名字。

    SQLite 生成的匿名约束在 Alembic ``batch_alter_table`` 里没法按名引用，
    到时候要改一个 CHECK 只能整表重建。命名规范让迁移脚本可以写
    ``op.drop_constraint("ck_accounts_role_allowed")``。
    """

    @pytest.mark.parametrize(
        ("table", "constraint"),
        [
            ("accounts", "ck_accounts_teacher_xor_student"),
            ("accounts", "ck_accounts_role_allowed"),
            ("teachers", "ck_teachers_teacherrole"),
            ("teachers", "ck_teachers_approvalstatus"),
            ("students", "ck_students_approvalstatus"),
            ("classes", "ck_classes_schoolstage"),
            ("student_parent_bindings", "uq_binding_student_parent"),
            ("teacher_class_subjects", "uq_teacher_class_subjects_teacher_id_class_id_subject"),
        ],
    )
    def test_constraint_name_present_in_ddl(
        self, engine: Engine, table: str, constraint: str
    ) -> None:
        with engine.connect() as conn:
            ddl = conn.execute(
                text("SELECT sql FROM sqlite_master WHERE name = :t"), {"t": table}
            ).scalar_one()
        assert constraint in ddl

    def test_homeroom_teacher_is_indexed(self, engine: Engine) -> None:
        """外键列没索引时，按班主任反查班级会全表扫描。"""
        with engine.connect() as conn:
            indexes = {
                row.name
                for row in conn.execute(
                    text("SELECT name FROM sqlite_master WHERE type = 'index' AND tbl_name = 'classes'")
                )
            }
        assert "ix_classes_homeroom_teacher_id" in indexes
