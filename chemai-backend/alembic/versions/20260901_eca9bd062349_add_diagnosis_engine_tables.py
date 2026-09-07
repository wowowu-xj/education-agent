"""add_diagnosis_engine_tables

Revision ID: eca9bd062349
Revises: abdf18d1111a
Create Date: 2026-09-01 21:12:21.082556+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'eca9bd062349'
down_revision: Union[str, Sequence[str], None] = 'abdf18d1111a'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级到当前版本"""
    op.create_table('barrier_configs',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('teacher_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='教师（唯一）'),
    sa.Column('concept_threshold', sa.Integer(), nullable=False, comment='概念理解型触发阈值'),
    sa.Column('reading_threshold', sa.Integer(), nullable=False, comment='审题障碍型触发阈值'),
    sa.Column('expression_threshold', sa.Integer(), nullable=False, comment='表述障碍型触发阈值'),
    sa.Column('mastery_threshold', sa.Integer(), nullable=False, comment='掌握度阈值'),
    sa.Column('auto_sync_to_student', sa.Boolean(), nullable=False, comment='是否自动同步到学生画像'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.ForeignKeyConstraint(['teacher_id'], ['teachers.id'], name=op.f('fk_barrier_configs_teacher_id_teachers'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_barrier_configs'))
    )
    with op.batch_alter_table('barrier_configs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_barrier_configs_teacher_id'), ['teacher_id'], unique=True)

    op.create_table('diagnosis_override_logs',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('student_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='学生'),
    sa.Column('old_profile', sa.JSON(), nullable=True, comment='覆盖前画像'),
    sa.Column('new_profile', sa.JSON(), nullable=True, comment='覆盖后画像'),
    sa.Column('reason', sa.Text(), nullable=False, comment='覆盖原因'),
    sa.Column('operator_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='操作教师'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='覆盖时间（UTC）'),
    sa.ForeignKeyConstraint(['operator_id'], ['teachers.id'], name=op.f('fk_diagnosis_override_logs_operator_id_teachers'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_diagnosis_override_logs_student_id_students'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_diagnosis_override_logs'))
    )
    with op.batch_alter_table('diagnosis_override_logs', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_diagnosis_override_logs_student_id'), ['student_id'], unique=False)

    op.create_table('parent_notifications',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('student_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='学生'),
    sa.Column('parent_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='家长'),
    sa.Column('type', sa.String(length=32), nullable=False, comment='通知类型（如 learning_plan）'),
    sa.Column('content', sa.Text(), nullable=False, comment='通知内容'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='发送时间（UTC）'),
    sa.Column('read_at', sa.DateTime(timezone=True), nullable=True, comment='已读时间（NULL 表示未读）'),
    sa.ForeignKeyConstraint(['parent_id'], ['parents.id'], name=op.f('fk_parent_notifications_parent_id_parents'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_parent_notifications_student_id_students'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_parent_notifications'))
    )
    with op.batch_alter_table('parent_notifications', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_parent_notifications_parent_id'), ['parent_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_parent_notifications_student_id'), ['student_id'], unique=False)

    op.create_table('student_answers',
    sa.Column('id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), autoincrement=True, nullable=False),
    sa.Column('student_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='学生'),
    sa.Column('exam_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='考试（即文档的「考试记录」）'),
    sa.Column('question_id', sa.BigInteger().with_variant(sa.Integer(), 'sqlite'), nullable=False, comment='题目'),
    sa.Column('is_correct', sa.Boolean(), nullable=False, comment='是否作答正确'),
    sa.Column('student_answer', sa.Text(), nullable=False, comment='学生作答内容'),
    sa.Column('barrier_type', sa.Enum('concept', 'reading', 'expression', name='barriertype', native_enum=False, create_constraint=True, length=16), nullable=True, comment='障碍类型'),
    sa.Column('misconception_category', sa.Enum('chemical_equilibrium', 'redox', 'mole_calculation', 'organic_chemistry', 'chemical_notation', 'structure_properties', name='misconceptioncategory', native_enum=False, create_constraint=True, length=32), nullable=True, comment='迷思概念类别'),
    sa.Column('confidence', sa.Float(), nullable=True, comment='诊断置信度（0–1）'),
    sa.Column('consecutive_errors', sa.Integer(), nullable=False, comment='连续错误次数'),
    sa.Column('consecutive_correct', sa.Integer(), nullable=False, comment='连续正确次数'),
    sa.Column('created_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='创建时间（UTC）'),
    sa.Column('updated_at', sa.DateTime(timezone=True), server_default=sa.text('(CURRENT_TIMESTAMP)'), nullable=False, comment='更新时间（UTC）'),
    sa.ForeignKeyConstraint(['exam_id'], ['exams.id'], name=op.f('fk_student_answers_exam_id_exams'), ondelete='CASCADE'),
    sa.ForeignKeyConstraint(['question_id'], ['questions.id'], name=op.f('fk_student_answers_question_id_questions'), ondelete='RESTRICT'),
    sa.ForeignKeyConstraint(['student_id'], ['students.id'], name=op.f('fk_student_answers_student_id_students'), ondelete='CASCADE'),
    sa.PrimaryKeyConstraint('id', name=op.f('pk_student_answers'))
    )
    with op.batch_alter_table('student_answers', schema=None) as batch_op:
        batch_op.create_index(batch_op.f('ix_student_answers_exam_id'), ['exam_id'], unique=False)
        batch_op.create_index(batch_op.f('ix_student_answers_student_id'), ['student_id'], unique=False)

    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.add_column(sa.Column('misconception_profile', sa.JSON(), nullable=True))
        batch_op.add_column(sa.Column('current_plan', sa.JSON(), nullable=True))


def downgrade() -> None:
    """降级到上一版本"""
    with op.batch_alter_table('students', schema=None) as batch_op:
        batch_op.drop_column('current_plan')
        batch_op.drop_column('misconception_profile')

    with op.batch_alter_table('student_answers', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_student_answers_student_id'))
        batch_op.drop_index(batch_op.f('ix_student_answers_exam_id'))

    op.drop_table('student_answers')
    with op.batch_alter_table('parent_notifications', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_parent_notifications_student_id'))
        batch_op.drop_index(batch_op.f('ix_parent_notifications_parent_id'))

    op.drop_table('parent_notifications')
    with op.batch_alter_table('diagnosis_override_logs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_diagnosis_override_logs_student_id'))

    op.drop_table('diagnosis_override_logs')
    with op.batch_alter_table('barrier_configs', schema=None) as batch_op:
        batch_op.drop_index(batch_op.f('ix_barrier_configs_teacher_id'))

    op.drop_table('barrier_configs')
