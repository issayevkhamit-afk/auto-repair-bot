"""Add users.username and ensure all auth columns exist (safe for partial DB)

Revision ID: b2c3d4e5f6a7
Revises: a1b2c3d4e5f6
Create Date: 2026-03-19

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa
from sqlalchemy import inspect, text


revision: str = 'b2c3d4e5f6a7'
down_revision: Union[str, None] = 'a1b2c3d4e5f6'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def _column_exists(table: str, column: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return column in [c["name"] for c in insp.get_columns(table)]


def _index_exists(index_name: str) -> bool:
    bind = op.get_bind()
    result = bind.execute(text(
        "SELECT 1 FROM pg_indexes WHERE indexname = :name"
    ), {"name": index_name})
    return result.fetchone() is not None


def _table_exists(table: str) -> bool:
    bind = op.get_bind()
    insp = inspect(bind)
    return table in insp.get_table_names()


def upgrade() -> None:
    # ── users table ──────────────────────────────────────────────────────────
    if not _column_exists("users", "username"):
        op.add_column("users", sa.Column("username", sa.String(), nullable=True))

    if not _column_exists("users", "status"):
        op.add_column("users", sa.Column("status", sa.String(),
                                          nullable=True, server_default="active"))

    if not _column_exists("users", "hashed_password"):
        op.add_column("users", sa.Column("hashed_password", sa.String(), nullable=True))

    # Create unique index for username only if it doesn't already exist
    if not _index_exists("ix_users_username"):
        op.create_index("ix_users_username", "users", ["username"], unique=True)

    # ── shops table ──────────────────────────────────────────────────────────
    shops_columns = {
        "logo_url":          sa.Column("logo_url",          sa.String(),  nullable=True),
        "pdf_template_data": sa.Column("pdf_template_data", sa.Text(),    nullable=True),
        "website":           sa.Column("website",           sa.String(),  nullable=True),
        "whatsapp":          sa.Column("whatsapp",          sa.String(),  nullable=True),
        "status":            sa.Column("status",            sa.String(),  nullable=True,
                                       server_default="active"),
        "plan":              sa.Column("plan",              sa.String(),  nullable=True,
                                       server_default="trial"),
        "created_at":        sa.Column("created_at",        sa.DateTime(), nullable=True),
    }
    for col_name, col_def in shops_columns.items():
        if not _column_exists("shops", col_name):
            op.add_column("shops", col_def)

    # ── system tables ────────────────────────────────────────────────────────
    if not _table_exists("global_ai_settings"):
        op.create_table(
            "global_ai_settings",
            sa.Column("id",                  sa.Integer(), nullable=False),
            sa.Column("system_prompt",       sa.Text(),    nullable=True),
            sa.Column("extraction_template", sa.Text(),    nullable=True),
            sa.Column("pricing_rules",       sa.Text(),    nullable=True),
            sa.Column("model_name",          sa.String(),  nullable=True),
            sa.Column("fallback_settings",   sa.Text(),    nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        if not _index_exists("ix_global_ai_settings_id"):
            op.create_index("ix_global_ai_settings_id", "global_ai_settings", ["id"], unique=False)

    if not _table_exists("system_logs"):
        op.create_table(
            "system_logs",
            sa.Column("id",         sa.Integer(), nullable=False),
            sa.Column("log_type",   sa.String(),  nullable=True, index=True),
            sa.Column("message",    sa.String(),  nullable=False),
            sa.Column("details",    sa.Text(),    nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        if not _index_exists("ix_system_logs_id"):
            op.create_index("ix_system_logs_id", "system_logs", ["id"], unique=False)
        if not _index_exists("ix_system_logs_log_type"):
            op.create_index("ix_system_logs_log_type", "system_logs", ["log_type"], unique=False)

    if not _table_exists("subscription_plans"):
        op.create_table(
            "subscription_plans",
            sa.Column("id",             sa.Integer(), nullable=False),
            sa.Column("name",           sa.String(),  nullable=True),
            sa.Column("price",          sa.String(),  nullable=True),
            sa.Column("estimate_limit", sa.Integer(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        if not _index_exists("ix_subscription_plans_id"):
            op.create_index("ix_subscription_plans_id", "subscription_plans", ["id"], unique=False)
        if not _index_exists("ix_subscription_plans_name"):
            op.create_index("ix_subscription_plans_name", "subscription_plans", ["name"], unique=True)


def downgrade() -> None:
    if _index_exists("ix_users_username"):
        op.drop_index("ix_users_username", table_name="users")
    if _column_exists("users", "username"):
        op.drop_column("users", "username")
