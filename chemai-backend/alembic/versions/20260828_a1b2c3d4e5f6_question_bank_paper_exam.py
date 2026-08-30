"""题库、试卷、考试数据表迁移

Revision ID: a1b2c3d4e5f6
Revises: dcc811e0f1a6
Create Date: 2026-08-28 10:00:00.000000+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, Sequence[str], None] = 'dcc811e0f1a6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级：创建题目、题库文件夹、试卷、考试相关表"""
    op.create_table('questions',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('teacher_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=True, comment='创建者 Teacher.id（可空）'),
    sa.Column('content', sa.Text(), nullable=False, comment='题干'),
    sa.Column('type', sa.Enum('single_choice', 'multi_choice', 'true_false', 'fill_blank', 'short_answer', 'essay', 'calculation', 'experiment', 'inference', name='questiontype', native_enum=False, create_constraint=True, length=32), nullable=False, comment='题型（9 种）'),
    sa.Column('options', sa.JSON(), nullable=True, comment='选项（JSON 数组，仅选择题）'),
    sa.Column('answer', sa.Text(), nullable=False, comment='标准答案'),
    sa.Column('analysis', sa.Text(), nullable=True, comment='解析'),
    sa.Column('knowledge_points', sa.JSON(), nullable=False, comment='知识点（JSON 数组）'),
    sa.Column('difficulty', sa.Enum('easy', 'medium', 'hard', 'competition', name='difficulty', native_enum=False, create_constraint=True, length=32), nullable=False, comment='难度（4 档）'),
    sa.Column('score', sa.Float(), nullable=False, comment='建议分值'),
    sa.Column('source_name', sa.String(length=200), nullable=True, comment='来源名称'),
    sa.Column('region', sa.String(length=100), nullable=True, comment='来源地区'),
    sa.Column('year', sa.Integer(), nullable=True, comment='来源年份'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间（NULL 表示未删除）'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_questions_teacher_id_teachers'), ondelete='SET NULL'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_questions'))
    )
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_questions_teacher_id'), ['teacher_id'], unique=False)

    op.create_table('question_sets',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('name', sa.String(length=200), nullable=False, comment='文件夹名称'),
    sa.Column('teacher_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='所属教师'),
    sa.Column('description', sa.String(length=500), nullable=True, comment='文件夹描述'),
    sa.Column('region', sa.String(length=100), nullable=True, comment='来源地区'),
    sa.Column('year', sa.Integer(), nullable=True, comment='来源年份'),
    sa.Column('is_preset', sa.Boolean(), nullable=False, comment='是否系统预设（不可删）'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间（NULL 表示未删除）'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_question_sets_teacher_id_teachers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_question_sets'))
    )
    with op.batch_alter_table('question_sets', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_question_sets_teacher_id'), ['teacher_id'], unique=False)

    op.create_table('question_set_items',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('question_set_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='题库文件夹'),
    sa.Column('question_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='题目'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序序号'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name=op.f('fk_question_set_items_question_id_questions'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_set_id'], ['question_sets.id'], name=op.f('fk_question_set_items_question_set_id_question_sets'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_question_set_items')),
    sa.UniqueConstraint('question_set_id', 'question_id', name='uq_question_set_items_set_qid')
    )
    with op.batch_alter_table('question_set_items', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_question_set_items_question_id'), ['question_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_question_set_items_question_set_id'), ['question_set_id'], unique=False)

    op.create_table('papers',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('title', sa.String(length=200), nullable=False, comment='试卷标题'),
    sa.Column('teacher_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='所属教师'),
    sa.Column('duration', sa.Integer(), nullable=True, comment='考试时长（分钟）'),
    sa.Column('status', sa.Enum('draft', 'locked', name='paperstatus', native_enum=False, create_constraint=True, length=32), nullable=False, comment='状态 draft/locked'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.Column('deleted_at', sa.DateTime(timezone=True), nullable=True, comment='软删除时间（NULL 表示未删除）'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_papers_teacher_id_teachers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_papers'))
    )
    with op.batch_alter_table('papers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_papers_teacher_id'), ['teacher_id'], unique=False)

    op.create_table('paper_questions',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('paper_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='试卷'),
    sa.Column('question_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='题目'),
    sa.Column('sort_order', sa.Integer(), nullable=False, comment='排序序号'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], name=op.f('fk_paper_questions_paper_id_papers'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name=op.f('fk_paper_questions_question_id_questions'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_paper_questions')),
    sa.UniqueConstraint('paper_id', 'question_id', name='uq_paper_questions_paper_qid')
    )
    with op.batch_alter_table('paper_questions', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_paper_questions_paper_id'), ['paper_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_paper_questions_question_id'), ['question_id'], unique=False)

    op.create_table('exams',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('paper_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='试卷（共享引用）'),
    sa.Column('class_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='班级'),
    sa.Column('exam_date', sa.DateTime(timezone=True), nullable=True, comment='考试时间'),
    sa.Column('status', sa.Enum('published', 'in_progress', 'grading', 'completed', 'archived', 'cancelled', name='examstatus', native_enum=False, create_constraint=True, length=32), nullable=False, comment='状态（6 态）'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.ForeignKeyConstraint(['class_id'], ['classes.id'], name=op.f('fk_exams_class_id_classes'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['paper_id'], ['papers.id'], name=op.f('fk_exams_paper_id_papers'), ondelete='RESTRICT'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_exams'))
    )
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_exams_class_id'), ['class_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_exams_paper_id'), ['paper_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_exams_status'), ['status'], unique=False)


def downgrade() -> None:
    """降级：删除题目、题库文件夹、试卷、考试相关表"""
    with op.batch_alter_table('exams', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_exams_status'))
        batch_op.drop_index(batch_op.f('ix_exams_paper_id'))
        batch_op.drop_index(batch_op.f('ix_exams_class_id'))

    op.drop_table('exams')
    with op.batch_alter_table('paper_questions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_paper_questions_question_id'))
        batch_op.drop_index(batch_op.f('ix_paper_questions_paper_id'))

    op.drop_table('paper_questions')
    with op.batch_alter_table('papers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_papers_teacher_id'))

    op.drop_table('papers')
    with op.batch_alter_table('question_set_items', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_question_set_items_question_set_id'))
        batch_op.drop_index(batch_op.f('ix_question_set_items_question_id'))

    op.drop_table('question_set_items')
    with op.batch_alter_table('question_sets', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_question_sets_teacher_id'))

    op.drop_table('question_sets')
    with op.batch_alter_table('questions', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_questions_teacher_id'))

    op.drop_table('questions')
