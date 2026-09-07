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


class BarrierType(str, Enum):
    """障碍类型（回答「怎么错」）——三分类。

    与 :class:`MisconceptionCategory`（回答「错在哪」）正交，诊断结果必须同时包含两维。
    """
    CONCEPT = "concept"          # 概念理解型
    READING = "reading"          # 审题障碍型
    EXPRESSION = "expression"    # 表述障碍型


# 障碍类型 → 中文描述（供学习计划生成时映射，见 diagnosis-learning-plan spec）。
BARRIER_TYPE_DISPLAY: dict[BarrierType, str] = {
    BarrierType.CONCEPT: "概念理解型-基础概念和原理掌握不扎实",
    BarrierType.READING: "审题障碍型-读题时容易忽略关键条件或掉入陷阱选项",
    BarrierType.EXPRESSION: "表述障碍型-化学用语书写不规范或答题逻辑不清晰",
}


class MisconceptionCategory(str, Enum):
    """迷思概念类别（回答「错在哪」）——六分类。"""
    CHEMICAL_EQUILIBRIUM = "chemical_equilibrium"  # 化学平衡
    REDOX = "redox"                                # 氧化还原
    MOLE_CALCULATION = "mole_calculation"          # 摩尔计算
    ORGANIC_CHEMISTRY = "organic_chemistry"        # 有机化学
    CHEMICAL_NOTATION = "chemical_notation"        # 化学用语
    STRUCTURE_PROPERTIES = "structure_properties"  # 物构知识
