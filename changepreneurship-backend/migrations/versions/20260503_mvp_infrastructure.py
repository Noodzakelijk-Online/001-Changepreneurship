"""add MVP readiness and action infrastructure

Revision ID: 20260503_mvp_infra
Revises: 479a67b65e65
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '20260503_mvp_infra'
down_revision = '479a67b65e65'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'venture',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('venture_type', sa.String(length=80), nullable=True),
        sa.Column('stage', sa.String(length=80), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_venture_user_id'), 'venture', ['user_id'], unique=False)

    op.create_table(
        'external_connection',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('platform', sa.String(length=80), nullable=False),
        sa.Column('connection_status', sa.String(length=40), nullable=False),
        sa.Column('encrypted_access_token', sa.Text(), nullable=True),
        sa.Column('encrypted_refresh_token', sa.Text(), nullable=True),
        sa.Column('scope', sa.Text(), nullable=True),
        sa.Column('expires_at', sa.DateTime(), nullable=True),
        sa.Column('permission_level', sa.Integer(), nullable=False),
        sa.Column('connected_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_external_connection_user_id'), 'external_connection', ['user_id'], unique=False)

    op.create_table(
        'data_consent_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('data_category', sa.String(length=120), nullable=False),
        sa.Column('consent_given', sa.Boolean(), nullable=False),
        sa.Column('consent_text_version', sa.String(length=80), nullable=False),
        sa.Column('legal_basis', sa.String(length=80), nullable=False),
        sa.Column('consented_at', sa.DateTime(), nullable=True),
        sa.Column('revoked_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_data_consent_log_user_id'), 'data_consent_log', ['user_id'], unique=False)

    op.create_table(
        'founder_readiness_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('financial_readiness', sa.Text(), nullable=False),
        sa.Column('time_capacity', sa.Text(), nullable=False),
        sa.Column('personal_readiness', sa.Text(), nullable=False),
        sa.Column('skills_experience', sa.Text(), nullable=False),
        sa.Column('execution_behaviour', sa.Text(), nullable=False),
        sa.Column('evidence_discipline', sa.Text(), nullable=False),
        sa.Column('communication_ability', sa.Text(), nullable=False),
        sa.Column('support_network', sa.Text(), nullable=False),
        sa.Column('founder_idea_fit', sa.Text(), nullable=False),
        sa.Column('founder_market_fit', sa.Text(), nullable=False),
        sa.Column('risk_awareness', sa.Text(), nullable=False),
        sa.Column('operational_discipline', sa.Text(), nullable=False),
        sa.Column('automation_leverage', sa.Text(), nullable=False),
        sa.Column('venture_readiness_status', sa.String(length=40), nullable=False),
        sa.Column('risk_level', sa.String(length=40), nullable=False),
        sa.Column('evidence_confidence', sa.String(length=40), nullable=False),
        sa.Column('next_step_eligibility', sa.String(length=80), nullable=False),
        sa.Column('external_readiness_status', sa.String(length=80), nullable=False),
        sa.Column('survival_risk_indicator', sa.String(length=40), nullable=False),
        sa.Column('founder_venture_fit_status', sa.String(length=80), nullable=False),
        sa.Column('route_confidence', sa.String(length=40), nullable=False),
        sa.Column('founder_type', sa.String(length=8), nullable=True),
        sa.Column('routing_state', sa.String(length=80), nullable=False),
        sa.Column('summary', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_founder_readiness_profile_user_id'), 'founder_readiness_profile', ['user_id'], unique=False)
    op.create_index(op.f('ix_founder_readiness_profile_venture_id'), 'founder_readiness_profile', ['venture_id'], unique=False)

    op.create_table(
        'phase_gate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('phase_id', sa.String(length=80), nullable=False),
        sa.Column('gate_status', sa.String(length=40), nullable=False),
        sa.Column('blocking_dimension', sa.String(length=120), nullable=True),
        sa.Column('blocking_reason', sa.Text(), nullable=True),
        sa.Column('unlock_condition', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('resolved_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_phase_gate_user_id'), 'phase_gate', ['user_id'], unique=False)
    op.create_index(op.f('ix_phase_gate_venture_id'), 'phase_gate', ['venture_id'], unique=False)

    op.create_table(
        'user_action',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('action_type', sa.String(length=80), nullable=False),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('title', sa.String(length=200), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('proposed_content', sa.Text(), nullable=False),
        sa.Column('approved_content', sa.Text(), nullable=True),
        sa.Column('approval_required', sa.Boolean(), nullable=False),
        sa.Column('external_platform', sa.String(length=80), nullable=True),
        sa.Column('external_account_id', sa.Integer(), nullable=True),
        sa.Column('estimated_cost', sa.Float(), nullable=True),
        sa.Column('actual_cost', sa.Float(), nullable=True),
        sa.Column('audit_log', sa.Text(), nullable=False),
        sa.Column('error_message', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('proposed_at', sa.DateTime(), nullable=True),
        sa.Column('approved_at', sa.DateTime(), nullable=True),
        sa.Column('executed_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['external_account_id'], ['external_connection.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_user_action_user_id'), 'user_action', ['user_id'], unique=False)
    op.create_index(op.f('ix_user_action_venture_id'), 'user_action', ['venture_id'], unique=False)


def downgrade():
    op.drop_index(op.f('ix_user_action_venture_id'), table_name='user_action')
    op.drop_index(op.f('ix_user_action_user_id'), table_name='user_action')
    op.drop_table('user_action')
    op.drop_index(op.f('ix_phase_gate_venture_id'), table_name='phase_gate')
    op.drop_index(op.f('ix_phase_gate_user_id'), table_name='phase_gate')
    op.drop_table('phase_gate')
    op.drop_index(op.f('ix_founder_readiness_profile_venture_id'), table_name='founder_readiness_profile')
    op.drop_index(op.f('ix_founder_readiness_profile_user_id'), table_name='founder_readiness_profile')
    op.drop_table('founder_readiness_profile')
    op.drop_index(op.f('ix_data_consent_log_user_id'), table_name='data_consent_log')
    op.drop_table('data_consent_log')
    op.drop_index(op.f('ix_external_connection_user_id'), table_name='external_connection')
    op.drop_table('external_connection')
    op.drop_index(op.f('ix_venture_user_id'), table_name='venture')
    op.drop_table('venture')
