"""Phase 6 Business Development — Sprint 12 migration."""
import sqlalchemy as sa
from alembic import op

revision = '20260512_01_sprint12'
down_revision = '20260511_01_sprint11'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'business_dev_data',
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
        'venture_environment',
        sa.Column('id',                 sa.Integer(),  nullable=False),
        sa.Column('user_id',            sa.Integer(),  nullable=False),
        sa.Column('venture_id',         sa.Integer(),  nullable=True),
        sa.Column('environment_data',   sa.JSON(),     nullable=False, server_default='{}'),
        sa.Column('readiness_score',    sa.Integer(),  nullable=True),
        sa.Column('operational_ready',  sa.Boolean(),  nullable=False, server_default=sa.false()),
        sa.Column('decision',           sa.String(30), nullable=True),
        sa.Column('generated_at',       sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['user.id'],           ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venture_id'], ['venture_record.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_venture_environment_user_id', 'venture_environment', ['user_id'])


def downgrade():
    op.drop_index('ix_venture_environment_user_id', table_name='venture_environment')
    op.drop_table('venture_environment')
    op.drop_table('business_dev_data')
