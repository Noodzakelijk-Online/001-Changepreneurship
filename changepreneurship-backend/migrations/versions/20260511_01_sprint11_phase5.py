"""Phase 5 Product Concept Testing — Sprint 11 migration."""
import sqlalchemy as sa
from alembic import op

revision = '20260511_01_sprint11'
down_revision = '20260510_01_sprint10'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'concept_test_data',
        sa.Column('id',         sa.Integer(),     nullable=False),
        sa.Column('user_id',    sa.Integer(),     nullable=False),
        sa.Column('venture_id', sa.Integer(),     nullable=True),
        sa.Column('responses',  sa.JSON(),        nullable=False, server_default='{}'),
        sa.Column('completed',  sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(),    nullable=False),
        sa.Column('updated_at', sa.DateTime(),    nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['user.id'],           ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venture_id'], ['venture_record.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('user_id'),
    )
    op.create_table(
        'concept_test_result',
        sa.Column('id',                     sa.Integer(),     nullable=False),
        sa.Column('user_id',                sa.Integer(),     nullable=False),
        sa.Column('venture_id',             sa.Integer(),     nullable=True),
        sa.Column('result_data',            sa.JSON(),        nullable=False, server_default='{}'),
        sa.Column('adoption_signal',        sa.String(20),    nullable=True),
        sa.Column('decision',               sa.String(20),    nullable=True),
        sa.Column('ready_for_business_dev', sa.Boolean(),     nullable=False, server_default=sa.false()),
        sa.Column('generated_at',           sa.DateTime(),    nullable=False),
        sa.ForeignKeyConstraint(['user_id'],    ['user.id'],           ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['venture_id'], ['venture_record.id'], ondelete='SET NULL'),
        sa.PrimaryKeyConstraint('id'),
    )
    op.create_index('ix_concept_test_result_user_id', 'concept_test_result', ['user_id'])


def downgrade():
    op.drop_index('ix_concept_test_result_user_id', table_name='concept_test_result')
    op.drop_table('concept_test_result')
    op.drop_table('concept_test_data')
