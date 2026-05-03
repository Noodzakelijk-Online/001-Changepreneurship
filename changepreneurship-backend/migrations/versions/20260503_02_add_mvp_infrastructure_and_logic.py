"""add MVP infrastructure and logic tables

Revision ID: add_mvp_infra_logic
Revises: add_resume_enrichment_fields
Create Date: 2026-05-03
"""
from alembic import op
import sqlalchemy as sa


revision = 'add_mvp_infra_logic'
down_revision = 'add_resume_enrichment_fields'
branch_labels = None
depends_on = None


def _timestamps():
    return [
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),
    ]


def upgrade() -> None:
    op.create_table(
        'venture',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=160), nullable=False),
        sa.Column('venture_type', sa.String(length=80), nullable=True),
        sa.Column('stage', sa.String(length=80), nullable=False),
        sa.Column('status', sa.String(length=30), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_venture_user_id', 'venture', ['user_id'], unique=False)

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
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_external_connection_user_id', 'external_connection', ['user_id'], unique=False)

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
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_data_consent_log_user_id', 'data_consent_log', ['user_id'], unique=False)

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
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_founder_readiness_profile_user_id', 'founder_readiness_profile', ['user_id'], unique=False)
    op.create_index('ix_founder_readiness_profile_venture_id', 'founder_readiness_profile', ['venture_id'], unique=False)

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
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_phase_gate_user_id', 'phase_gate', ['user_id'], unique=False)
    op.create_index('ix_phase_gate_venture_id', 'phase_gate', ['venture_id'], unique=False)

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
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_action_user_id', 'user_action', ['user_id'], unique=False)
    op.create_index('ix_user_action_venture_id', 'user_action', ['venture_id'], unique=False)

    op.create_table(
        'evidence_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('evidence_type', sa.String(length=80), nullable=False),
        sa.Column('source', sa.String(length=160), nullable=True),
        sa.Column('claim', sa.Text(), nullable=False),
        sa.Column('evidence_strength', sa.String(length=40), nullable=False),
        sa.Column('confidence', sa.String(length=40), nullable=False),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_evidence_record_user_id', 'evidence_record', ['user_id'], unique=False)
    op.create_index('ix_evidence_record_venture_id', 'evidence_record', ['venture_id'], unique=False)

    op.create_table(
        'assumption_record',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('assumption_text', sa.Text(), nullable=False),
        sa.Column('category', sa.String(length=80), nullable=False),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('risk_level', sa.String(length=40), nullable=False),
        sa.Column('linked_evidence_id', sa.Integer(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(['linked_evidence_id'], ['evidence_record.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_assumption_record_user_id', 'assumption_record', ['user_id'], unique=False)
    op.create_index('ix_assumption_record_venture_id', 'assumption_record', ['venture_id'], unique=False)

    op.create_table(
        'user_fit_assessment',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('fit_category', sa.String(length=40), nullable=False),
        sa.Column('reason', sa.Text(), nullable=True),
        sa.Column('allowed_mode', sa.String(length=80), nullable=False),
        sa.Column('blocked_actions_json', sa.Text(), nullable=False),
        sa.Column('redirect_route', sa.String(length=80), nullable=True),
        sa.Column('unlock_condition', sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_user_fit_assessment_user_id', 'user_fit_assessment', ['user_id'], unique=False)
    op.create_index('ix_user_fit_assessment_venture_id', 'user_fit_assessment', ['venture_id'], unique=False)

    op.create_table(
        'action_permission_policy',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('permission_scope', sa.String(length=80), nullable=False),
        sa.Column('execution_mode', sa.String(length=80), nullable=False),
        sa.Column('requires_external_effect', sa.Boolean(), nullable=False),
        sa.Column('requires_explicit_approval', sa.Boolean(), nullable=False),
        sa.Column('allowed_operations_json', sa.Text(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['action_id'], ['user_action.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_action_permission_policy_action_id', 'action_permission_policy', ['action_id'], unique=False)
    op.create_index('ix_action_permission_policy_user_id', 'action_permission_policy', ['user_id'], unique=False)

    op.create_table(
        'action_outcome',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('action_id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('outcome_status', sa.String(length=60), nullable=False),
        sa.Column('outcome_summary', sa.Text(), nullable=True),
        sa.Column('next_follow_up_at', sa.DateTime(), nullable=True),
        sa.Column('next_recommended_action_type', sa.String(length=80), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(['action_id'], ['user_action.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_action_outcome_action_id', 'action_outcome', ['action_id'], unique=False)
    op.create_index('ix_action_outcome_user_id', 'action_outcome', ['user_id'], unique=False)
    op.create_index('ix_action_outcome_venture_id', 'action_outcome', ['venture_id'], unique=False)

    op.create_table(
        'benchmark_event',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('event_type', sa.String(length=80), nullable=False),
        sa.Column('route', sa.String(length=80), nullable=True),
        sa.Column('founder_type', sa.String(length=8), nullable=True),
        sa.Column('phase_id', sa.String(length=80), nullable=True),
        sa.Column('action_type', sa.String(length=80), nullable=True),
        sa.Column('outcome_status', sa.String(length=80), nullable=True),
        sa.Column('metadata_json', sa.Text(), nullable=False),
        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_benchmark_event_user_id', 'benchmark_event', ['user_id'], unique=False)
    op.create_index('ix_benchmark_event_venture_id', 'benchmark_event', ['venture_id'], unique=False)

    op.create_table(
        'cost_estimate',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('action_id', sa.Integer(), nullable=True),
        sa.Column('estimated_direct_cost', sa.Float(), nullable=False),
        sa.Column('estimated_billed_price', sa.Float(), nullable=False),
        sa.Column('actual_direct_cost', sa.Float(), nullable=True),
        sa.Column('actual_billed_price', sa.Float(), nullable=True),
        sa.Column('pricing_multiplier', sa.Float(), nullable=False),
        sa.Column('pricing_basis', sa.String(length=160), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['action_id'], ['user_action.id']),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_cost_estimate_user_id', 'cost_estimate', ['user_id'], unique=False)
    op.create_index('ix_cost_estimate_venture_id', 'cost_estimate', ['venture_id'], unique=False)
    op.create_index('ix_cost_estimate_action_id', 'cost_estimate', ['action_id'], unique=False)

    op.create_table(
        'spending_cap',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('cap_type', sa.String(length=40), nullable=False),
        sa.Column('amount', sa.Float(), nullable=False),
        sa.Column('currency', sa.String(length=8), nullable=False),
        sa.Column('requires_approval_above_amount', sa.Boolean(), nullable=False),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_spending_cap_user_id', 'spending_cap', ['user_id'], unique=False)
    op.create_index('ix_spending_cap_venture_id', 'spending_cap', ['venture_id'], unique=False)

    op.create_table(
        'professional_review_requirement',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('category', sa.String(length=80), nullable=False),
        sa.Column('trigger_reason', sa.Text(), nullable=False),
        sa.Column('required_before_action_type', sa.String(length=80), nullable=True),
        sa.Column('status', sa.String(length=40), nullable=False),
        sa.Column('professional_notes', sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_professional_review_requirement_user_id', 'professional_review_requirement', ['user_id'], unique=False)
    op.create_index('ix_professional_review_requirement_venture_id', 'professional_review_requirement', ['venture_id'], unique=False)

    op.create_table(
        'venture_connection_mode',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('venture_id', sa.Integer(), nullable=True),
        sa.Column('connection_mode', sa.String(length=40), nullable=False),
        sa.Column('explanation', sa.Text(), nullable=True),
        *_timestamps(),
        sa.ForeignKeyConstraint(['user_id'], ['user.id']),
        sa.ForeignKeyConstraint(['venture_id'], ['venture.id']),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_venture_connection_mode_user_id', 'venture_connection_mode', ['user_id'], unique=False)
    op.create_index('ix_venture_connection_mode_venture_id', 'venture_connection_mode', ['venture_id'], unique=False)


def downgrade() -> None:
    for index_name, table_name in [
        ('ix_venture_connection_mode_venture_id', 'venture_connection_mode'),
        ('ix_venture_connection_mode_user_id', 'venture_connection_mode'),
        ('ix_professional_review_requirement_venture_id', 'professional_review_requirement'),
        ('ix_professional_review_requirement_user_id', 'professional_review_requirement'),
        ('ix_spending_cap_venture_id', 'spending_cap'),
        ('ix_spending_cap_user_id', 'spending_cap'),
        ('ix_cost_estimate_action_id', 'cost_estimate'),
        ('ix_cost_estimate_venture_id', 'cost_estimate'),
        ('ix_cost_estimate_user_id', 'cost_estimate'),
        ('ix_benchmark_event_venture_id', 'benchmark_event'),
        ('ix_benchmark_event_user_id', 'benchmark_event'),
        ('ix_action_outcome_venture_id', 'action_outcome'),
        ('ix_action_outcome_user_id', 'action_outcome'),
        ('ix_action_outcome_action_id', 'action_outcome'),
        ('ix_action_permission_policy_user_id', 'action_permission_policy'),
        ('ix_action_permission_policy_action_id', 'action_permission_policy'),
        ('ix_user_fit_assessment_venture_id', 'user_fit_assessment'),
        ('ix_user_fit_assessment_user_id', 'user_fit_assessment'),
        ('ix_assumption_record_venture_id', 'assumption_record'),
        ('ix_assumption_record_user_id', 'assumption_record'),
        ('ix_evidence_record_venture_id', 'evidence_record'),
        ('ix_evidence_record_user_id', 'evidence_record'),
        ('ix_user_action_venture_id', 'user_action'),
        ('ix_user_action_user_id', 'user_action'),
        ('ix_phase_gate_venture_id', 'phase_gate'),
        ('ix_phase_gate_user_id', 'phase_gate'),
        ('ix_founder_readiness_profile_venture_id', 'founder_readiness_profile'),
        ('ix_founder_readiness_profile_user_id', 'founder_readiness_profile'),
        ('ix_data_consent_log_user_id', 'data_consent_log'),
        ('ix_external_connection_user_id', 'external_connection'),
        ('ix_venture_user_id', 'venture'),
    ]:
        op.drop_index(index_name, table_name=table_name)

    for table_name in [
        'venture_connection_mode',
        'professional_review_requirement',
        'spending_cap',
        'cost_estimate',
        'benchmark_event',
        'action_outcome',
        'action_permission_policy',
        'user_fit_assessment',
        'assumption_record',
        'evidence_record',
        'user_action',
        'phase_gate',
        'founder_readiness_profile',
        'data_consent_log',
        'external_connection',
        'venture',
    ]:
        op.drop_table(table_name)
