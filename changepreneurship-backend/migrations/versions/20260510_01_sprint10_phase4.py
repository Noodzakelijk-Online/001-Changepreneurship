"""
Sprint 10 — Phase 4 Business Pillars tables

Revision: 20260510_01_sprint10
Down revision: 20260509_01_sprint9

Creates:
  business_pillars_data      — user's pillar answers
  business_pillars_blueprint — generated Business Pillars Blueprint
"""
revision = '20260510_01_sprint10'
down_revision = '20260509_01_sprint9'
branch_labels = None
depends_on = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'business_pillars_data',
        sa.Column('id',         sa.Integer, primary_key=True),
        sa.Column('user_id',    sa.Integer,
                  sa.ForeignKey('user.id', ondelete='CASCADE'),
                  nullable=False, unique=True),
        sa.Column('venture_id', sa.Integer,
                  sa.ForeignKey('venture_record.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('pillars',    sa.JSON, nullable=False, server_default='{}'),
        sa.Column('completed',  sa.Boolean, nullable=False, server_default='false'),
        sa.Column('created_at', sa.DateTime, nullable=False,
                  server_default=sa.text('NOW()')),
        sa.Column('updated_at', sa.DateTime, nullable=False,
                  server_default=sa.text('NOW()')),
    )

    op.create_table(
        'business_pillars_blueprint',
        sa.Column('id',                       sa.Integer, primary_key=True),
        sa.Column('user_id',                  sa.Integer,
                  sa.ForeignKey('user.id', ondelete='CASCADE'),
                  nullable=False),
        sa.Column('venture_id',               sa.Integer,
                  sa.ForeignKey('venture_record.id', ondelete='SET NULL'),
                  nullable=True),
        sa.Column('blueprint_data',           sa.JSON, nullable=False),
        sa.Column('coherence_score',          sa.Integer, nullable=True),
        sa.Column('ready_for_concept_testing', sa.Boolean, nullable=False,
                  server_default='false'),
        sa.Column('generated_at',             sa.DateTime, nullable=False,
                  server_default=sa.text('NOW()')),
    )


def downgrade():
    op.drop_table('business_pillars_blueprint')
    op.drop_table('business_pillars_data')
