"""add exam_status_transitions audit table

Revision ID: abdf18d1111a
Revises: a1b2c3d4e5f6
Create Date: 2026-08-29 22:46:43.890079+08:00

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'abdf18d1111a'
down_revision: Union[str, Sequence[str], None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """升级到当前版本"""
    op.create_table(
        'exam_status_transitions',
        sa.Column(
            'exam_id',
            sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
            nullable=False,
            comment='考试',
        ),
        sa.Column(
            'from_status',
            sa.Enum(
                'published', 'in_progress', 'grading', 'completed', 'archived',
                'cancelled', name='examstatus', native_enum=False,
                create_constraint=True, length=32,
            ),
            nullable=False,
            comment='迁移前状态',
        ),
        sa.Column(
            'to_status',
            sa.Enum(
                'published', 'in_progress', 'grading', 'completed', 'archived',
                'cancelled', name='examstatus', native_enum=False,
                create_constraint=True, length=32,
            ),
            nullable=False,
            comment='迁移后状态',
        ),
        sa.Column(
            'operator_id',
            sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
            nullable=False,
            comment='操作教师',
        ),
        sa.Column(
            'created_at',
            sa.DateTime(timezone=True),
            server_default=sa.text('(CURRENT_TIMESTAMP)'),
            nullable=False,
            comment='迁移时间（UTC）',
        ),
        sa.Column(
            'id',
            sa.BigInteger().with_variant(sa.Integer(), 'sqlite'),
            autoincrement=True,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ['exam_id'], ['exams.id'],
            name=op.f('fk_exam_status_transitions_exam_id_exams'),
            ondelete='CASCADE',
        ),
        sa.ForeignKeyConstraint(
            ['operator_id'], ['teachers.id'],
            name=op.f('fk_exam_status_transitions_operator_id_teachers'),
            ondelete='RESTRICT',
        ),
        sa.PrimaryKeyConstraint('id', name=op.f('pk_exam_status_transitions')),
    )


def downgrade() -> None:
    """降级到上一版本"""
    op.drop_table('exam_status_transitions')
