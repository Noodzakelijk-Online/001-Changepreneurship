"""
Sprint 6 Migration: BenchmarkData table.

CEO (Section 13.1): Anonymised cohort aggregate for benchmark intelligence.
GDPR: No user_id column — cohort_key is a hash.

Revision: 20260506_01_benchmark_data
Down revision: 20260503_01_vr
"""
from alembic import op
import sqlalchemy as sa

revision = '20260506_01_benchmark'
down_revision = '20260503_01_vr'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'benchmark_data',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),

        # Anonymised cohort (no user_id — GDPR safe)
        sa.Column('cohort_key',   sa.String(64),  nullable=False),
        sa.Column('cohort_label', sa.String(100), nullable=False),

        sa.Column('metric_type',  sa.String(40),  nullable=False),
        sa.Column('metric_value', sa.JSON(),       nullable=False),
        sa.Column('sample_size',  sa.Integer(),    nullable=False, server_default='0'),

        sa.Column('last_updated',  sa.DateTime(),  server_default=sa.func.now(), onupdate=sa.func.now()),
        sa.Column('is_anonymized', sa.Boolean(),   nullable=False, server_default='true'),
    )

    op.create_index('ix_benchmark_cohort_key', 'benchmark_data', ['cohort_key'])

    op.create_unique_constraint(
        'uq_benchmark_cohort_metric',
        'benchmark_data',
        ['cohort_key', 'metric_type'],
    )


def downgrade():
    op.drop_constraint('uq_benchmark_cohort_metric', 'benchmark_data', type_='unique')
    op.drop_index('ix_benchmark_cohort_key', table_name='benchmark_data')
    op.drop_table('benchmark_data')
