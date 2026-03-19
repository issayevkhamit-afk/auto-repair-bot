"""Add RBAC, branding fields, and system tables

Revision ID: a1b2c3d4e5f6
Revises: e0802b7f3694
Create Date: 2026-03-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'a1b2c3d4e5f6'
down_revision: Union[str, None] = 'e0802b7f3694'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ---- users table: add RBAC and auth columns -------------------------
    op.add_column('users',
        sa.Column('status', sa.String(), nullable=True, server_default='active'))
    op.add_column('users',
        sa.Column('hashed_password', sa.String(), nullable=True))

    # ---- shops table: add branding and SaaS meta columns ----------------
    op.add_column('shops',
        sa.Column('logo_url', sa.String(), nullable=True))
    op.add_column('shops',
        sa.Column('pdf_template_data', sa.Text(), nullable=True))
    op.add_column('shops',
        sa.Column('website', sa.String(), nullable=True))
    op.add_column('shops',
        sa.Column('whatsapp', sa.String(), nullable=True))
    op.add_column('shops',
        sa.Column('status', sa.String(), nullable=True, server_default='active'))
    op.add_column('shops',
        sa.Column('plan', sa.String(), nullable=True, server_default='trial'))
    op.add_column('shops',
        sa.Column('created_at', sa.DateTime(), nullable=True))

    # ---- global_ai_settings table ---------------------------------------
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

    # ---- system_logs table -----------------------------------------------
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

    # ---- subscription_plans table ----------------------------------------
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
    op.drop_index(op.f('ix_subscription_plans_name'), table_name='subscription_plans')
    op.drop_index(op.f('ix_subscription_plans_id'), table_name='subscription_plans')
    op.drop_table('subscription_plans')

    op.drop_index(op.f('ix_system_logs_log_type'), table_name='system_logs')
    op.drop_index(op.f('ix_system_logs_id'), table_name='system_logs')
    op.drop_table('system_logs')

    op.drop_index(op.f('ix_global_ai_settings_id'), table_name='global_ai_settings')
    op.drop_table('global_ai_settings')

    op.drop_column('shops', 'created_at')
    op.drop_column('shops', 'plan')
    op.drop_column('shops', 'status')
    op.drop_column('shops', 'whatsapp')
    op.drop_column('shops', 'website')
    op.drop_column('shops', 'pdf_template_data')
    op.drop_column('shops', 'logo_url')

    op.drop_column('users', 'hashed_password')
    op.drop_column('users', 'status')
