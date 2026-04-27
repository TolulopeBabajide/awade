"""add_parental_consents_table

Revision ID: b3f92c1d4e87
Revises: a8a7efde9d3c
Create Date: 2026-04-27 00:00:00.000000

AWD-GRC-01 — COPPA compliance: parental consent record before ChildProfile creation.
One row per parent. Cascades on user deletion.
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'b3f92c1d4e87'
down_revision: Union[str, Sequence[str], None] = 'a8a7efde9d3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        'parental_consents',
        sa.Column('consent_id', sa.Integer(), autoincrement=True, nullable=False),
        sa.Column('parent_id', sa.Integer(), nullable=False),
        sa.Column('consented_at', sa.DateTime(), nullable=False, server_default=sa.text('now()')),
        sa.Column('ip_address', sa.String(length=45), nullable=True),
        sa.Column('consent_version', sa.String(length=20), nullable=False, server_default='1.0'),
        sa.ForeignKeyConstraint(['parent_id'], ['users.user_id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('consent_id'),
        sa.UniqueConstraint('parent_id', name='uq_parental_consents_parent_id'),
    )
    op.create_index(
        'ix_parental_consents_parent_id',
        'parental_consents',
        ['parent_id'],
        unique=True,
    )


def downgrade() -> None:
    op.drop_index('ix_parental_consents_parent_id', table_name='parental_consents')
    op.drop_table('parental_consents')
