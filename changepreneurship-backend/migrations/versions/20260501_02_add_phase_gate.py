"""add phase gate

Revision ID: 20260501_02_pg
Revises: 20260501_01_frp
Create Date: 2026-05-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260501_02_pg'
down_revision = '20260501_01_frp'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'phase_gate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        # Phase 1-7 maps to CEO's 7-phase journey
        sa.Column('phase_number', sa.SmallInteger(), nullable=False),

        # LOCKED | UNLOCKED | IN_PROGRESS | COMPLETED | BLOCKED
        sa.Column('status', sa.String(length=20), nullable=False, server_default='LOCKED'),

        # Active blockers on this phase gate
        # [{blocker_id, type, reason, unlock_condition}]
        sa.Column('blockers', sa.JSON(), nullable=False, server_default='[]'),

        # Conditions that must ALL be met to unlock this phase
        # [{condition, met}]
        sa.Column('unlock_conditions', sa.JSON(), nullable=False, server_default='[]'),

        # Human-readable summary of why blocked
        sa.Column('blocking_reason', sa.Text(), nullable=True),

        sa.Column('unlocked_at', sa.DateTime(), nullable=True),
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id', 'phase_number', name='uq_phase_gate_user_phase'),
    )
    op.create_index('ix_pg_user_phase', 'phase_gate', ['user_id', 'phase_number'])
    op.create_index('ix_pg_user_status', 'phase_gate', ['user_id', 'status'])


def downgrade() -> None:
    op.drop_index('ix_pg_user_status', table_name='phase_gate')
    op.drop_index('ix_pg_user_phase', table_name='phase_gate')
    op.drop_table('phase_gate')
