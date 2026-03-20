"""Add RBAC, branding fields, and system tables (idempotent / safe for partial migrations)

Revision ID: a1b2c3d4e5f6
Revises: e0802b7f3694
Create Date: 2026-03-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e0802b7f3694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _has_column(table: str, column: str) -> bool:
    """Return True if `column` already exists on `table` in the live DB."""
    bind = op.get_bind()
    insp = inspect(bind)
    cols = [c["name"] for c in insp.get_columns(table)]
    return column in cols


def _has_table(table: str) -> bool:
    """Return True if `table` already exists in the live DB."""
    bind = op.get_bind()
    insp = inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    # ---- users table: RBAC and auth columns ----------------------------------
    if not _has_column('users', 'status'):
        op.add_column('users',
            sa.Column('status', sa.String(), nullable=True, server_default='active'))

    if not _has_column('users', 'hashed_password'):
        op.add_column('users',
            sa.Column('hashed_password', sa.String(), nullable=True))

    if not _has_column('users', 'username'):
        op.add_column('users',
            sa.Column('username', sa.String(), nullable=True))
        # Create index separately (not inline) to avoid issues on partial runs
        op.create_index('ix_users_username', 'users', ['username'], unique=True)

    # ---- shops table: branding and SaaS meta columns -------------------------
    for col_name, col_def in [
        ('logo_url',         sa.Column('logo_url', sa.String(), nullable=True)),
        ('pdf_template_data',sa.Column('pdf_template_data', sa.Text(), nullable=True)),
        ('website',          sa.Column('website', sa.String(), nullable=True)),
        ('whatsapp',         sa.Column('whatsapp', sa.String(), nullable=True)),
        ('status',           sa.Column('status', sa.String(), nullable=True, server_default='active')),
        ('plan',             sa.Column('plan', sa.String(), nullable=True, server_default='trial')),
        ('created_at',       sa.Column('created_at', sa.DateTime(), nullable=True)),
    ]:
        if not _has_column('shops', col_name):
            op.add_column('shops', col_def)

    # ---- global_ai_settings table --------------------------------------------
    if not _has_table('global_ai_settings'):
        op.create_table(
            'global_ai_settings',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('system_prompt', sa.Text(), nullable=True),
            sa.Column('extraction_template', sa.Text(), nullable=True),
            sa.Column('pricing_rules', sa.Text(), nullable=True),
            sa.Column('model_name', sa.String(), nullable=True),
            sa.Column('fallback_settings', sa.Text(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_global_ai_settings_id'), 'global_ai_settings', ['id'], unique=False)

    # ---- system_logs table ---------------------------------------------------
    if not _has_table('system_logs'):
        op.create_table(
            'system_logs',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('log_type', sa.String(), nullable=True),
            sa.Column('message', sa.String(), nullable=False),
            sa.Column('details', sa.Text(), nullable=True),
            sa.Column('created_at', sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_system_logs_id'), 'system_logs', ['id'], unique=False)
        op.create_index(op.f('ix_system_logs_log_type'), 'system_logs', ['log_type'], unique=False)

    # ---- subscription_plans table --------------------------------------------
    if not _has_table('subscription_plans'):
        op.create_table(
            'subscription_plans',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('name', sa.String(), nullable=True),
            sa.Column('price', sa.String(), nullable=True),
            sa.Column('estimate_limit', sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint('id'),
        )
        op.create_index(op.f('ix_subscription_plans_id'), 'subscription_plans', ['id'], unique=False)
        op.create_index(op.f('ix_subscription_plans_name'), 'subscription_plans', ['name'], unique=True)


def downgrade() -> None:
    if _has_table('subscription_plans'):
        op.drop_index(op.f('ix_subscription_plans_name'), table_name='subscription_plans')
        op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
        op.drop_table('subscription_plans')

    if _has_table('system_logs'):
        op.drop_index(op.f('ix_system_logs_log_type'), table_name='system_logs')
        op.drop_index(op.f('ix_system_logs_id'), table_name='system_logs')
        op.drop_table('system_logs')

    if _has_table('global_ai_settings'):
        op.drop_index(op.f('ix_global_ai_settings_id'), table_name='global_ai_settings')
        op.drop_table('global_ai_settings')

    for col in ['created_at', 'plan', 'status', 'whatsapp', 'website', 'pdf_template_data', 'logo_url']:
        if _has_column('shops', col):
            op.drop_column('shops', col)

    if _has_column('users', 'hashed_password'):
        op.drop_column('users', 'hashed_password')
    if _has_column('users', 'status'):
        op.drop_column('users', 'status')
