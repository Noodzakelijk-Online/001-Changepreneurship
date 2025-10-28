"""expand password hash length

Revision ID: expand_password_hash_len
Revises: 479a67b65e65
Create Date: 2025-10-28 10:25:00
"""
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision = 'expand_password_hash_len'
down_revision = '479a67b65e65'
branch_labels = None
depends_on = None

def upgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password_hash', type_=sa.String(length=300))


def downgrade() -> None:
    with op.batch_alter_table('user') as batch_op:
        batch_op.alter_column('password_hash', type_=sa.String(length=128))
