"""Phase 7 Business Prototype Testing — Sprint 13 migration."""
import sqlalchemy as sa
from alembic import op

revision = '20260513_01_sprint13'
down_revision = '20260512_01_sprint12'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'prototype_test_data',
        sa.Column('id',         sa.Integer(),  nullable=False),
        sa.Column('user_id',    sa.Integer(),  nullable=False),
        sa.Column('venture_id', sa.Integer(),  nullable=True),
        sa.Column('responses',  sa.JSON(),     nullable=False, server_default='{}'),
        sa.Column('completed',  sa.Boolean(),  nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(), nullable=False),
        sa.Column('updated_at', sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['user.id'],           ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venture_id'], ['venture_record.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_table(
        'prototype_test_result',
        sa.Column('id',               sa.Integer(),     nullable=False),
        sa.Column('user_id',          sa.Integer(),     nullable=False),
        sa.Column('venture_id',       sa.Integer(),     nullable=True),
        sa.Column('result_data',      sa.JSON(),        nullable=False, server_default='{}'),
        sa.Column('scale_readiness',  sa.String(20),    nullable=True),
        sa.Column('scale_score',      sa.Integer(),     nullable=True),
        sa.Column('decision',         sa.String(30),    nullable=True),
        sa.Column('ready_to_scale',   sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column('generated_at',     sa.DateTime(),    nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['user.id'],           ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venture_id'], ['venture_record.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )


def downgrade():
    op.drop_table('prototype_test_result')
    op.drop_table('prototype_test_data')
