"""Add assessment modules schema for 20+ modules support

Revision ID: 20260326_01
Revises: 479a67b65e65
Create Date: 2026-03-26 16:45:00.000000

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = '20260326_01'
down_revision = '479a67b65e65'
branch_labels = None
depends_on = None


def upgrade():
    # Create assessment_modules table
    op.create_table(
        'assessment_modules',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.String(100), nullable=False, unique=True),
        sa.Column('module_name', sa.String(200), nullable=False),
        sa.Column('category', sa.String(50), nullable=False),  # 'self_insight', 'strategy', 'execution', etc.
        sa.Column('order', sa.Integer(), nullable=False),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('estimated_duration', sa.Integer(), nullable=True),  # in minutes
        sa.Column('is_active', sa.Boolean(), default=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('module_id', name='uq_assessment_modules_module_id')
    )
    op.create_index('ix_assessment_modules_category', 'assessment_modules', ['category'])
    op.create_index('ix_assessment_modules_module_id', 'assessment_modules', ['module_id'])

    # Create module_responses table
    op.create_table(
        'module_responses',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('user_id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.String(100), nullable=False),
        sa.Column('section_id', sa.String(100), nullable=True),
        sa.Column('question_id', sa.String(100), nullable=True),
        sa.Column('response_value', sa.Text(), nullable=True),  # JSON
        sa.Column('completed_at', sa.DateTime(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), default=sa.func.now(), onupdate=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['user_id'], ['user.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['module_id'], ['assessment_modules.module_id'], ondelete='CASCADE')
    )
    op.create_index('ix_module_responses_user_id', 'module_responses', ['user_id'])
    op.create_index('ix_module_responses_module_id', 'module_responses', ['module_id'])
    op.create_index('ix_module_responses_user_module', 'module_responses', ['user_id', 'module_id'])

    # Create module_interconnections table
    op.create_table(
        'module_interconnections',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('source_module_id', sa.String(100), nullable=False),
        sa.Column('source_field', sa.String(200), nullable=False),
        sa.Column('target_module_id', sa.String(100), nullable=False),
        sa.Column('target_field', sa.String(200), nullable=False),
        sa.Column('transformation_logic', sa.Text(), nullable=True),  # JSON
        sa.Column('label', sa.String(200), nullable=True),
        sa.Column('description', sa.Text(), nullable=True),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['source_module_id'], ['assessment_modules.module_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['target_module_id'], ['assessment_modules.module_id'], ondelete='CASCADE')
    )
    op.create_index('ix_module_interconnections_source', 'module_interconnections', ['source_module_id'])
    op.create_index('ix_module_interconnections_target', 'module_interconnections', ['target_module_id'])

    # Create context_references table
    op.create_table(
        'context_references',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('module_id', sa.String(100), nullable=False),
        sa.Column('reference_module_id', sa.String(100), nullable=False),
        sa.Column('reference_field', sa.String(200), nullable=False),
        sa.Column('display_label', sa.String(200), nullable=False),
        sa.Column('display_order', sa.Integer(), nullable=False),
        sa.Column('created_at', sa.DateTime(), default=sa.func.now()),
        sa.PrimaryKeyConstraint('id'),
        sa.ForeignKeyConstraint(['module_id'], ['assessment_modules.module_id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['reference_module_id'], ['assessment_modules.module_id'], ondelete='CASCADE')
    )
    op.create_index('ix_context_references_module', 'context_references', ['module_id'])

    # Add new columns to entrepreneur_profile for module-based data
    op.add_column('entrepreneur_profile', sa.Column('module_progress', sa.Text(), nullable=True))  # JSON
    op.add_column('entrepreneur_profile', sa.Column('interconnection_data', sa.Text(), nullable=True))  # JSON
    op.add_column('entrepreneur_profile', sa.Column('module_insights', sa.Text(), nullable=True))  # JSON


def downgrade():
    # Remove columns from entrepreneur_profile
    op.drop_column('entrepreneur_profile', 'module_insights')
    op.drop_column('entrepreneur_profile', 'interconnection_data')
    op.drop_column('entrepreneur_profile', 'module_progress')

    # Drop tables
    op.drop_table('context_references')
    op.drop_table('module_interconnections')
    op.drop_table('module_responses')
    op.drop_table('assessment_modules')
