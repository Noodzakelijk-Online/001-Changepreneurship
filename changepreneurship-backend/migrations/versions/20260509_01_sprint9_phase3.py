"""
Sprint 9 Migration: CompetitorEntry + MarketContext + MarketValidityReport.

Phase 3 Market Research data layer.
- competitor_entry    — user's competitor map entries
- market_context      — market-level inputs (pain, WTP, segment)
- market_validity_report — generated Market Validity Report (JSON)

Revision: 20260509_01_sprint9
Down revision: 20260507_01_sprint7
"""
from alembic import op
import sqlalchemy as sa

revision = '20260509_01_sprint9'
down_revision = '20260507_01_sprint7'
branch_labels = None
depends_on = None


def upgrade():
    # ── competitor_entry ────────────────────────────────────────────────────
    op.create_table(
        'competitor_entry',
        sa.Column('id',         sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id',    sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('venture_id', sa.Integer(), sa.ForeignKey('venture_record.id', ondelete='SET NULL'), nullable=True),

        sa.Column('name',        sa.String(200), nullable=False),
        sa.Column('description', sa.String(500), nullable=True),
        sa.Column('strengths',   sa.String(500), nullable=True),
        sa.Column('weaknesses',  sa.String(500), nullable=True),
        sa.Column('positioning', sa.String(200), nullable=True),
        sa.Column('is_direct',   sa.Boolean(),   nullable=False, server_default='true'),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_competitor_entry_user_id', 'competitor_entry', ['user_id'])

    # ── market_context ──────────────────────────────────────────────────────
    op.create_table(
        'market_context',
        sa.Column('id',         sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id',    sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False, unique=True),
        sa.Column('venture_id', sa.Integer(), sa.ForeignKey('venture_record.id', ondelete='SET NULL'), nullable=True),

        sa.Column('target_segment',        sa.String(300), nullable=True),
        sa.Column('pain_intensity',        sa.String(20),  nullable=False, server_default='MEDIUM'),
        sa.Column('willingness_to_pay',    sa.Boolean(),   nullable=False, server_default='false'),
        sa.Column('estimated_price_range', sa.String(100), nullable=True),
        sa.Column('market_timing',         sa.String(200), nullable=True),
        sa.Column('market_size_note',      sa.String(500), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_market_context_user_id', 'market_context', ['user_id'])

    # ── market_validity_report ──────────────────────────────────────────────
    op.create_table(
        'market_validity_report',
        sa.Column('id',         sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id',    sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),
        sa.Column('venture_id', sa.Integer(), sa.ForeignKey('venture_record.id', ondelete='CASCADE'), nullable=False),

        sa.Column('report_data',  sa.JSON(),    nullable=False),
        sa.Column('generated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),

        sa.UniqueConstraint('user_id', 'venture_id', name='uq_mvr_user_venture'),
    )
    op.create_index('ix_market_validity_report_user_id', 'market_validity_report', ['user_id'])


def downgrade():
    op.drop_table('market_validity_report')
    op.drop_table('market_context')
    op.drop_table('competitor_entry')
