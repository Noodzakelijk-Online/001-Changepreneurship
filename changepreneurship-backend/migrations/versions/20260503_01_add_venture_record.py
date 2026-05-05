"""
Sprint 3 Migration: VentureRecord + EvidenceItem tables.

VentureRecord — Layer 2 Venture Record System (CEO Section 7.1).
EvidenceItem  — Typed evidence with strength classification (CEO Section 2.5).

Revision: 20260503_01_venture_record
Down revision: 20260502_02_frp_rename
"""
from alembic import op
import sqlalchemy as sa

revision = '20260503_01_vr'
down_revision = '20260502_02_frp_rename'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # venture_record
    # ------------------------------------------------------------------
    op.create_table(
        'venture_record',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('version', sa.Integer(), nullable=False, default=1),
        sa.Column('is_active', sa.Boolean(), nullable=False, default=True),

        # Raw input (user words)
        sa.Column('idea_raw', sa.Text()),
        sa.Column('idea_clarified', sa.Text()),

        # Structured outputs (AI + user approved)
        sa.Column('problem_statement', sa.Text()),
        sa.Column('target_user_hypothesis', sa.Text()),
        sa.Column('value_proposition', sa.Text()),

        # Typing
        sa.Column('venture_type', sa.String(20)),  # FORPROFIT/NONPROFIT/SOCIAL/LOCAL/DEEPTECH/HYBRID
        sa.Column('founder_motivation_summary', sa.Text()),

        # Working lists
        sa.Column('assumptions', sa.JSON(), nullable=False, default=list),
        sa.Column('open_questions', sa.JSON(), nullable=False, default=list),

        # Status
        sa.Column('status', sa.String(20), nullable=False, default='DRAFT'),
        # DRAFT/CLARIFIED/VALIDATED/TESTING/OPERATIONAL/PAUSED/ARCHIVED

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), server_default=sa.func.now(), onupdate=sa.func.now()),
    )

    op.create_index('ix_venture_record_user_id', 'venture_record', ['user_id'])
    op.create_index('ix_venture_record_active', 'venture_record', ['user_id', 'is_active'])

    # ------------------------------------------------------------------
    # evidence_item
    # ------------------------------------------------------------------
    op.create_table(
        'evidence_item',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('venture_id', sa.Integer(), sa.ForeignKey('venture_record.id', ondelete='CASCADE'), nullable=True),

        # Evidence classification
        sa.Column('evidence_type', sa.String(30), nullable=False),
        # INTERVIEW/SURVEY/PAYMENT/SIGNUP/LOI/PILOT/REPEAT/REFERRAL/THIRDPARTY

        sa.Column('strength', sa.String(30), nullable=False, default='BELIEF'),
        # BELIEF/OPINION/DESK_RESEARCH/AI_RESEARCH/INDIRECT/DIRECT/BEHAVIORAL
        # Hierarchy: BELIEF < OPINION < DESK_RESEARCH < AI_RESEARCH < INDIRECT < DIRECT < BEHAVIORAL

        sa.Column('description', sa.Text(), nullable=False),
        sa.Column('source', sa.String(255)),
        sa.Column('evidence_date', sa.Date()),

        sa.Column('is_validated', sa.Boolean(), nullable=False, default=False),
        sa.Column('validation_notes', sa.Text()),

        # Which dimensions of FounderReadinessProfile this evidence affects
        sa.Column('affects_dimensions', sa.JSON(), nullable=False, default=list),

        sa.Column('created_at', sa.DateTime(), server_default=sa.func.now()),
    )

    op.create_index('ix_evidence_item_user_id', 'evidence_item', ['user_id'])
    op.create_index('ix_evidence_item_venture_id', 'evidence_item', ['venture_id'])
    op.create_index('ix_evidence_item_strength', 'evidence_item', ['strength'])


def downgrade():
    op.drop_index('ix_evidence_item_strength', 'evidence_item')
    op.drop_index('ix_evidence_item_venture_id', 'evidence_item')
    op.drop_index('ix_evidence_item_user_id', 'evidence_item')
    op.drop_table('evidence_item')

    op.drop_index('ix_venture_record_active', 'venture_record')
    op.drop_index('ix_venture_record_user_id', 'venture_record')
    op.drop_table('venture_record')
