"""add founder readiness profile

Revision ID: 20260501_01_frp
Revises: add_resume_enrichment_fields
Create Date: 2026-05-01 00:00:00
"""
from alembic import op
import sqlalchemy as sa


revision = '20260501_01_frp'
down_revision = 'add_resume_enrichment_fields'
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'founder_readiness_profile',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, server_default='1'),
        sa.Column('is_latest', sa.Boolean(), nullable=False, server_default='1'),

        # 13 Typed Dimensions — score 0-100, level 0-5
        # Level: 0=Watch/Healthy, 1=OK, 2=Warning, 3=Soft Block, 4=Hard Block, 5=Hard Stop
        sa.Column('financial_readiness_score', sa.SmallInteger(), nullable=True),
        sa.Column('financial_readiness_level', sa.SmallInteger(), nullable=True),

        sa.Column('time_capacity_score', sa.SmallInteger(), nullable=True),
        sa.Column('time_capacity_level', sa.SmallInteger(), nullable=True),

        sa.Column('personal_stability_score', sa.SmallInteger(), nullable=True),
        sa.Column('personal_stability_level', sa.SmallInteger(), nullable=True),

        sa.Column('motivation_quality_score', sa.SmallInteger(), nullable=True),
        sa.Column('motivation_quality_level', sa.SmallInteger(), nullable=True),

        sa.Column('skills_experience_score', sa.SmallInteger(), nullable=True),
        sa.Column('skills_experience_level', sa.SmallInteger(), nullable=True),

        sa.Column('founder_idea_fit_score', sa.SmallInteger(), nullable=True),
        sa.Column('founder_idea_fit_level', sa.SmallInteger(), nullable=True),

        sa.Column('founder_market_fit_score', sa.SmallInteger(), nullable=True),
        sa.Column('founder_market_fit_level', sa.SmallInteger(), nullable=True),

        sa.Column('idea_clarity_score', sa.SmallInteger(), nullable=True),
        sa.Column('idea_clarity_level', sa.SmallInteger(), nullable=True),

        sa.Column('market_validity_score', sa.SmallInteger(), nullable=True),
        sa.Column('market_validity_level', sa.SmallInteger(), nullable=True),

        sa.Column('business_model_score', sa.SmallInteger(), nullable=True),
        sa.Column('business_model_level', sa.SmallInteger(), nullable=True),

        sa.Column('strategic_position_score', sa.SmallInteger(), nullable=True),
        sa.Column('strategic_position_level', sa.SmallInteger(), nullable=True),

        sa.Column('evidence_quality_score', sa.SmallInteger(), nullable=True),
        sa.Column('evidence_quality_level', sa.SmallInteger(), nullable=True),

        sa.Column('network_mentorship_score', sa.SmallInteger(), nullable=True),
        sa.Column('network_mentorship_level', sa.SmallInteger(), nullable=True),

        # Composite result — worst-case wins, NEVER average
        sa.Column('overall_readiness_level', sa.SmallInteger(), nullable=False, server_default='0'),

        # Routing output
        # CONTINUE|STABILIZE|LOW_CAPITAL|OPERATIONS_CLEANUP|IMPACT_SOCIAL|
        # DEEP_TECH|DEBT_CONSCIOUS|CORPORATE_TRANSITION|ACCELERATE|HARD_STOP
        sa.Column('recommended_route', sa.String(length=30), nullable=False, server_default='CONTINUE'),

        # Founder type A-P (CEO Section 2.2)
        sa.Column('founder_type', sa.String(length=2), nullable=True),

        # Active blockers — JSONB array of {type, dimension, severity, reason,
        #   what_is_blocked, what_is_allowed, unlock_condition}
        sa.Column('active_blockers', sa.JSON(), nullable=False, server_default='[]'),

        # Compensation rules applied — JSONB array
        sa.Column('compensation_rules_applied', sa.JSON(), nullable=False, server_default='[]'),

        # AI narrative (Layer 3) — generated AFTER rule engine ran
        sa.Column('ai_narrative', sa.Text(), nullable=True),
        sa.Column('ai_confidence', sa.String(length=20), nullable=True, server_default='LOW'),

        # Raw AI response for debugging/audit
        sa.Column('raw_ai_analysis', sa.JSON(), nullable=True),

        # Whether burnout or overload signal was detected
        sa.Column('burnout_signal_detected', sa.Boolean(), nullable=False, server_default='0'),
        sa.Column('overload_signal_detected', sa.Boolean(), nullable=False, server_default='0'),

        # Special scenario tag (A-F from CEO Section 4.5)
        sa.Column('detected_scenario', sa.String(length=30), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=True),
        sa.Column('updated_at', sa.DateTime(), nullable=True),

        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_frp_user_latest', 'founder_readiness_profile', ['user_id', 'is_latest'])
    op.create_index('ix_frp_user_version', 'founder_readiness_profile', ['user_id', 'version'])


def downgrade() -> None:
    op.drop_index('ix_frp_user_version', table_name='founder_readiness_profile')
    op.drop_index('ix_frp_user_latest', table_name='founder_readiness_profile')
    op.drop_table('founder_readiness_profile')
