"""
Sprint 2 Migration: UserAction + BlockerEvent tables.

UserAction — Trusted Action System (CEO Section 13.2)
  State machine: PROPOSED → REVIEWED → APPROVED → QUEUED → EXECUTED → OUTCOME_RECORDED
  OR:                       → REJECTED
  OR:                       → EXPIRED
  OR:                       → FAILED (after QUEUED/EXECUTED)

BlockerEvent — Immutable audit log of every blocker activation and resolution.

Revision: 20260502_01_user_action_blocker
Down revision: 20260501_02_pg
"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# Revision identifiers
revision = '20260502_01_ub'
down_revision = '20260501_02_pg'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # user_action
    # ------------------------------------------------------------------
    op.create_table(
        'user_action',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),

        # What / why / where
        sa.Column('action_type', sa.String(80), nullable=False),
        sa.Column('action_data', sa.JSON(), nullable=True),
        sa.Column('rationale', sa.Text(), nullable=True),
        sa.Column('external_platform', sa.String(80), nullable=True),
        sa.Column('external_account_id', sa.String(255), nullable=True),
        sa.Column('content_hash', sa.String(64), nullable=True),  # SHA-256 for dedup

        # State machine
        sa.Column('approval_status', sa.String(30), nullable=False, server_default='PROPOSED'),
        # PROPOSED / REVIEWED / APPROVED / QUEUED / EXECUTED / OUTCOME_RECORDED
        # / REJECTED / EXPIRED / FAILED / CANCELLED

        # Timestamps
        sa.Column('proposed_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('reviewed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('queued_at', sa.DateTime(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('outcome_recorded_at', sa.DateTime(), nullable=True),
        sa.Column('rejected_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),

        # Outputs
        sa.Column('result_data', sa.JSON(), nullable=True),
        sa.Column('failure_reason', sa.Text(), nullable=True),
        sa.Column('rejection_reason', sa.Text(), nullable=True),
        sa.Column('cost_credits', sa.Integer(), nullable=False, server_default='0'),

        # Immutable audit trail — append-only JSONB list of {event, at, by, data}
        sa.Column('audit_trail', sa.JSON(), nullable=False, server_default='[]'),
    )
    op.create_index('ix_user_action_user_id', 'user_action', ['user_id'])
    op.create_index('ix_user_action_status', 'user_action', ['approval_status'])
    op.create_index('ix_user_action_type', 'user_action', ['action_type'])
    op.create_index('ix_user_action_content_hash', 'user_action', ['user_id', 'content_hash'])

    # ------------------------------------------------------------------
    # blocker_event
    # ------------------------------------------------------------------
    op.create_table(
        'blocker_event',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),

        # Classification
        sa.Column('blocker_type', sa.String(80), nullable=False),
        sa.Column('dimension', sa.String(80), nullable=True),
        sa.Column('severity_level', sa.Integer(), nullable=False),  # 0-5
        sa.Column('source_service', sa.String(80), nullable=True),  # which engine triggered it

        # Trigger context
        sa.Column('trigger_signal', sa.JSON(), nullable=True),  # what data caused it
        sa.Column('what_is_blocked', sa.JSON(), nullable=True),
        sa.Column('what_is_allowed', sa.JSON(), nullable=True),
        sa.Column('unlock_condition', sa.Text(), nullable=True),

        # Lifecycle
        sa.Column('triggered_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.Column('resolution_type', sa.String(50), nullable=True),
        # RESOLVED / OVERRIDDEN_BY_ADMIN / EXPIRED / SUPERSEDED

        # FK to the assessment that triggered it (optional)
        sa.Column('founder_readiness_profile_id', sa.Integer(), nullable=True),
    )
    op.create_index('ix_blocker_event_user_id', 'blocker_event', ['user_id'])
    op.create_index('ix_blocker_event_active', 'blocker_event', ['user_id', 'resolved_at'])
    op.create_index('ix_blocker_event_type', 'blocker_event', ['blocker_type'])


def downgrade():
    op.drop_table('blocker_event')
    op.drop_table('user_action')
