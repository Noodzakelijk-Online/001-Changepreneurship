"""
Sprint 2 Migration: Rename FounderReadinessProfile columns to match Phase1RuleEngine.

Phase1RuleEngine.Phase1Result uses:
  - legal_employment (not strategic_position)
  - health_energy    (not evidence_quality)
  - burnout_signal   (not burnout_signal_detected)
  - overload_signal  (not overload_signal_detected)

This migration aligns the DB columns with the engine's field names.
SQLite supports RENAME COLUMN since 3.25 (2018). PostgreSQL supports it too.

Revision: 20260502_02_frp_rename
Down revision: 20260502_01_ub
"""
from alembic import op

revision = '20260502_02_frp_rename'
down_revision = '20260502_01_ub'
branch_labels = None
depends_on = None

_TABLE = 'founder_readiness_profile'


def upgrade():
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        batch_op.alter_column('strategic_position_score', new_column_name='legal_employment_score')
        batch_op.alter_column('strategic_position_level', new_column_name='legal_employment_level')
        batch_op.alter_column('evidence_quality_score',   new_column_name='health_energy_score')
        batch_op.alter_column('evidence_quality_level',   new_column_name='health_energy_level')
        batch_op.alter_column('burnout_signal_detected',  new_column_name='burnout_signal')
        batch_op.alter_column('overload_signal_detected', new_column_name='overload_signal')


def downgrade():
    with op.batch_alter_table(_TABLE, schema=None) as batch_op:
        batch_op.alter_column('legal_employment_score', new_column_name='strategic_position_score')
        batch_op.alter_column('legal_employment_level', new_column_name='strategic_position_level')
        batch_op.alter_column('health_energy_score',    new_column_name='evidence_quality_score')
        batch_op.alter_column('health_energy_level',    new_column_name='evidence_quality_level')
        batch_op.alter_column('burnout_signal',         new_column_name='burnout_signal_detected')
        batch_op.alter_column('overload_signal',        new_column_name='overload_signal_detected')
