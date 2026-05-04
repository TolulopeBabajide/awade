"""grc09_audit_log_actor_id_nullable

GRC-09: Make admin_audit_logs.actor_id nullable with ON DELETE SET NULL so that
deleting an admin user does not cascade-delete their audit trail.  This preserves
the audit log for compliance purposes (GDPR Art. 5(1)(e), NDPR, POPIA) while
preventing a FK constraint violation on user deletion.

Revision ID: f3a1c9d2b847
Revises: a8a7efde9d3c
Create Date: 2026-05-04

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'f3a1c9d2b847'
down_revision: Union[str, Sequence[str], None] = 'a8a7efde9d3c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Drop the existing non-nullable FK constraint on actor_id, then recreate it
    # as nullable with ON DELETE SET NULL.
    #
    # SQLite (used in tests) does not support ALTER COLUMN, so we use batch mode
    # which rewrites the table.  PostgreSQL supports it natively via batch as well.
    with op.batch_alter_table('admin_audit_logs', schema=None) as batch_op:
        batch_op.alter_column(
            'actor_id',
            existing_type=sa.Integer(),
            nullable=True,
        )
        # Drop the old FK (no ondelete clause) and recreate with SET NULL.
        batch_op.drop_constraint('fk_audit_log_actor', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_audit_log_actor',
            'users',
            ['actor_id'],
            ['user_id'],
            ondelete='SET NULL',
        )


def downgrade() -> None:
    # Restore NOT NULL and drop the SET NULL FK, replacing with a plain FK.
    # NOTE: rows where actor_id IS NULL (from a prior user deletion) cannot be
    # reverted to NOT NULL — a downgrade on a live database with NULL actor_ids
    # will fail.  Run only on a clean database or after back-filling actor_id.
    with op.batch_alter_table('admin_audit_logs', schema=None) as batch_op:
        batch_op.drop_constraint('fk_audit_log_actor', type_='foreignkey')
        batch_op.create_foreign_key(
            'fk_audit_log_actor',
            'users',
            ['actor_id'],
            ['user_id'],
        )
        batch_op.alter_column(
            'actor_id',
            existing_type=sa.Integer(),
            nullable=False,
        )
