"""
Sprint 7 Migration: ExternalConnection + DataConsentLog + Venture tables.

ExternalConnection — encrypted OAuth tokens for external platform accounts.
DataConsentLog     — GDPR consent audit trail (append-only).
Venture            — business entity, separate from User.

Revision: 20260507_01_sprint7_safety
Down revision: 20260506_01_benchmark
"""
from alembic import op
import sqlalchemy as sa

revision = '20260507_01_sprint7'
down_revision = '20260506_01_benchmark'
branch_labels = None
depends_on = None


def upgrade():
    # ------------------------------------------------------------------
    # external_connection — encrypted OAuth account connections
    # ------------------------------------------------------------------
    op.create_table(
        'external_connection',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),

        sa.Column('platform',           sa.String(40),  nullable=False),
        sa.Column('connection_status',  sa.String(20),  nullable=False, server_default='PENDING'),

        # Encrypted at rest — never plaintext in prod
        sa.Column('encrypted_access_token',  sa.Text(), nullable=True),
        sa.Column('encrypted_refresh_token', sa.Text(), nullable=True),

        sa.Column('scope',              sa.Text(),   nullable=True),
        sa.Column('permission_level',   sa.String(20), nullable=False, server_default='DRAFT'),

        sa.Column('external_account_email', sa.String(255), nullable=True),
        sa.Column('external_account_id',    sa.String(255), nullable=True),
        sa.Column('external_display_name',  sa.String(255), nullable=True),

        sa.Column('connected_at', sa.DateTime(), nullable=True),
        sa.Column('expires_at',   sa.DateTime(), nullable=True),
        sa.Column('revoked_at',   sa.DateTime(), nullable=True),
        sa.Column('last_used_at', sa.DateTime(), nullable=True),

        sa.Column('created_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at', sa.DateTime(), nullable=False, server_default=sa.func.now()),
    )
    op.create_index('ix_external_connection_user_id', 'external_connection', ['user_id'])

    # ------------------------------------------------------------------
    # data_consent_log — GDPR consent audit trail (append-only)
    # ------------------------------------------------------------------
    op.create_table(
        'data_consent_log',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),

        sa.Column('data_category',        sa.String(40),  nullable=False),
        sa.Column('consent_given',        sa.Boolean(),   nullable=False),
        sa.Column('consent_text_version', sa.String(20),  nullable=False, server_default='v1.0'),
        sa.Column('legal_basis',          sa.String(30),  nullable=False, server_default='CONSENT'),
        sa.Column('context',              sa.JSON(),      nullable=True),
        sa.Column('consented_at',         sa.DateTime(),  nullable=False, server_default=sa.func.now()),
        sa.Column('revokes_record_id',    sa.Integer(),   nullable=True),
    )
    op.create_index('ix_data_consent_log_user_id',  'data_consent_log', ['user_id'])
    op.create_index('ix_data_consent_log_category', 'data_consent_log', ['user_id', 'data_category'])

    # ------------------------------------------------------------------
    # venture — business entity (separate from user)
    # ------------------------------------------------------------------
    op.create_table(
        'venture',
        sa.Column('id', sa.Integer(), primary_key=True, autoincrement=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('user.id', ondelete='CASCADE'), nullable=False),

        sa.Column('venture_name',        sa.String(200), nullable=True),
        sa.Column('venture_description', sa.Text(),      nullable=True),
        sa.Column('venture_type',        sa.String(20),  nullable=True),
        sa.Column('venture_stage',       sa.String(20),  nullable=False, server_default='IDEA'),
        sa.Column('status',              sa.String(20),  nullable=False, server_default='ACTIVE'),
        sa.Column('is_primary',          sa.Boolean(),   nullable=False, server_default='true'),
        sa.Column('notes',               sa.Text(),      nullable=True),

        sa.Column('venture_record_id', sa.Integer(),
                  sa.ForeignKey('venture_record.id', ondelete='SET NULL'), nullable=True),

        sa.Column('created_at',    sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('updated_at',    sa.DateTime(), nullable=False, server_default=sa.func.now()),
        sa.Column('archived_at',   sa.DateTime(), nullable=True),
        sa.Column('completed_at',  sa.DateTime(), nullable=True),
    )
    op.create_index('ix_venture_user_id', 'venture', ['user_id'])


def downgrade():
    op.drop_index('ix_venture_user_id',         table_name='venture')
    op.drop_table('venture')

    op.drop_index('ix_data_consent_log_category', table_name='data_consent_log')
    op.drop_index('ix_data_consent_log_user_id',  table_name='data_consent_log')
    op.drop_table('data_consent_log')

    op.drop_index('ix_external_connection_user_id', table_name='external_connection')
    op.drop_table('external_connection')
