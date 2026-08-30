# -*- coding: utf-8 -*-
"""
核心枚举定义

约定：**库内存储的是枚举成员值（小写下划线），不是成员名**。
映射到列时必须走 :func:`app.models.base.enum_type`，它会同时保证
存值和生成 CHECK 约束。
"""
from enum import Enum


class TeacherRole(str, Enum):
    """教师角色枚举（含 4 种子角色）"""
    ADMIN = "admin"                    # 系统管理员
    ACADEMIC_ADMIN = "academic_admin"  # 教务管理员
    SUBJECT_LEAD = "subject_lead"      # 学科组长
    TEACHER = "teacher"                # 普通教师


# 角色中文展示映射（供前端和 API 响应使用）
TEACHER_ROLE_DISPLAY: dict[TeacherRole, str] = {
    TeacherRole.ADMIN: "系统管理员",
    TeacherRole.ACADEMIC_ADMIN: "教务管理员",
    TeacherRole.SUBJECT_LEAD: "学科组长",
    TeacherRole.TEACHER: "普通教师",
}


class ApprovalStatus(str, Enum):
    """审批状态枚举（教师入驻、学生注册通用）"""
    PENDING = "pending"      # 待审批
    APPROVED = "approved"    # 已通过
    REJECTED = "rejected"    # 已拒绝


class ParentRelation(str, Enum):
    """亲子关系枚举"""
    FATHER = "father"        # 父亲
    MOTHER = "mother"        # 母亲
    GUARDIAN = "guardian"    # 其他监护人


class SchoolStage(str, Enum):
    """学段"""
    JUNIOR = "junior"        # 初中
    SENIOR = "senior"        # 高中


# Account.role 的取值域。
# Account 同时服务教师和学生，所以不是单一枚举：教师侧取 TeacherRole，
# 学生侧固定为 "student"。Parent 不进 Account 表，因此不含 "parent"。
STUDENT_ROLE = "student"
ACCOUNT_ROLE_VALUES: tuple[str, ...] = tuple(role.value for role in TeacherRole) + (
    STUDENT_ROLE,
)


class QuestionType(str, Enum):
    """题目类型（九种题型）"""
    SINGLE_CHOICE = "single_choice"      # 单项选择题
    MULTI_CHOICE = "multi_choice"        # 多项选择题
    TRUE_FALSE = "true_false"            # 判断题
    FILL_BLANK = "fill_blank"            # 填空题
    SHORT_ANSWER = "short_answer"        # 简答题
    ESSAY = "essay"                      # 论述题
    CALCULATION = "calculation"          # 计算题
    EXPERIMENT = "experiment"            # 实验题
    INFERENCE = "inference"              # 推断题


class Difficulty(str, Enum):
    """题目难度（四档）"""
    EASY = "easy"                  # 简单
    MEDIUM = "medium"              # 中等
    HARD = "hard"                  # 困难
    COMPETITION = "competition"    # 竞赛


class PaperStatus(str, Enum):
    """试卷状态（两层状态机第一层）"""
    DRAFT = "draft"        # 草稿（可编辑）
    LOCKED = "locked"      # 已发布（只读）


class ExamStatus(str, Enum):
    """考试状态（两层状态机第二层，按班实例）"""
    PUBLISHED = "published"      # 已发布
    IN_PROGRESS = "in_progress"  # 作答中
    GRADING = "grading"          # 批阅中
    COMPLETED = "completed"      # 已完成
    ARCHIVED = "archived"        # 已归档
    CANCELLED = "cancelled"      # 已取消
