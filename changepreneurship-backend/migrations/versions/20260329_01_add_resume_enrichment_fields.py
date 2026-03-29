"""add resume enrichment fields

Revision ID: add_resume_enrichment_fields
Revises: expand_password_hash_len
Create Date: 2026-03-29 18:40:00
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_resume_enrichment_fields'
down_revision = 'expand_password_hash_len'
branch_labels = None
depends_on = None


def upgrade() -> None:
    with op.batch_alter_table('entrepreneur_profile') as batch_op:
        batch_op.add_column(sa.Column('resume_data', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('resume_analysis', sa.Text(), nullable=True))
        batch_op.add_column(sa.Column('resume_uploaded_at', sa.DateTime(), nullable=True))


def downgrade() -> None:
    with op.batch_alter_table('entrepreneur_profile') as batch_op:
        batch_op.drop_column('resume_uploaded_at')
        batch_op.drop_column('resume_analysis')
        batch_op.drop_column('resume_data')