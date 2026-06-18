"""add lembaga and billing

Revision ID: 004
Revises: 003
Create Date: 2026-06-17
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "004"
down_revision: Union[str, None] = "003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 0. If using PostgreSQL, check and add 'super_admin' value to 'userrole' enum type
    if conn.dialect.name == "postgresql":
        try:
            result = conn.execute(sa.text(
                "SELECT 1 FROM pg_type t "
                "JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = 'userrole' AND e.enumlabel = 'super_admin'"
            )).first()
            if not result:
                op.execute("COMMIT")
                op.execute("ALTER TYPE userrole ADD VALUE 'super_admin'")
        except Exception:
            pass

    # 1. Create table 'lembaga'
    if "lembaga" not in tables:
        op.create_table(
            "lembaga",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("credits", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_lembaga_id"), "lembaga", ["id"], unique=False)
        op.create_index(op.f("ix_lembaga_name"), "lembaga", ["name"], unique=True)

    # 2. Create table 'role_permissions'
    if "role_permissions" not in tables:
        op.create_table(
            "role_permissions",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("role", sa.String(length=50), nullable=False),
            sa.Column("permission_key", sa.String(length=100), nullable=False),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_role_permissions_id"), "role_permissions", ["id"], unique=False)
        op.create_index(op.f("ix_role_permissions_role"), "role_permissions", ["role"], unique=False)
        op.create_index(op.f("ix_role_permissions_permission_key"), "role_permissions", ["permission_key"], unique=False)

    # 3. Create table 'payment_logs'
    if "payment_logs" not in tables:
        op.create_table(
            "payment_logs",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("lembaga_id", sa.Integer(), nullable=False),
            sa.Column("amount", sa.Float(), nullable=False),
            sa.Column("credits_added", sa.Integer(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="success"),
            sa.Column("reference_no", sa.String(length=100), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["lembaga_id"], ["lembaga.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_payment_logs_id"), "payment_logs", ["id"], unique=False)

    # 4. Add 'lembaga_id' to users
    columns_users = [c["name"] for c in inspector.get_columns("users")]
    if "lembaga_id" not in columns_users:
        op.add_column("users", sa.Column("lembaga_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_users_lembaga", "users", "lembaga", ["lembaga_id"], ["id"])

    # 5. Add 'lembaga_id' to scan_sessions
    columns_sessions = [c["name"] for c in inspector.get_columns("scan_sessions")]
    if "lembaga_id" not in columns_sessions:
        op.add_column("scan_sessions", sa.Column("lembaga_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_sessions_lembaga", "scan_sessions", "lembaga", ["lembaga_id"], ["id"])

    # 6. Add 'lembaga_id' to reports
    columns_reports = [c["name"] for c in inspector.get_columns("reports")]
    if "lembaga_id" not in columns_reports:
        op.add_column("reports", sa.Column("lembaga_id", sa.Integer(), nullable=True))
        op.create_foreign_key("fk_reports_lembaga", "reports", "lembaga", ["lembaga_id"], ["id"])


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 1. Remove foreign keys and columns from 'reports', 'scan_sessions', 'users'
    if "reports" in tables:
        columns = [c["name"] for c in inspector.get_columns("reports")]
        if "lembaga_id" in columns:
            try:
                op.drop_constraint("fk_reports_lembaga", "reports", type_="foreignkey")
            except Exception:
                pass
            op.drop_column("reports", "lembaga_id")

    if "scan_sessions" in tables:
        columns = [c["name"] for c in inspector.get_columns("scan_sessions")]
        if "lembaga_id" in columns:
            try:
                op.drop_constraint("fk_sessions_lembaga", "scan_sessions", type_="foreignkey")
            except Exception:
                pass
            op.drop_column("scan_sessions", "lembaga_id")

    if "users" in tables:
        columns = [c["name"] for c in inspector.get_columns("users")]
        if "lembaga_id" in columns:
            try:
                op.drop_constraint("fk_users_lembaga", "users", type_="foreignkey")
            except Exception:
                pass
            op.drop_column("users", "lembaga_id")

    # 2. Drop table 'payment_logs'
    if "payment_logs" in tables:
        op.drop_index(op.f("ix_payment_logs_id"), table_name="payment_logs")
        op.drop_table("payment_logs")

    # 3. Drop table 'role_permissions'
    if "role_permissions" in tables:
        op.drop_index(op.f("ix_role_permissions_permission_key"), table_name="role_permissions")
        op.drop_index(op.f("ix_role_permissions_role"), table_name="role_permissions")
        op.drop_index(op.f("ix_role_permissions_id"), table_name="role_permissions")
        op.drop_table("role_permissions")

    # 4. Drop table 'lembaga'
    if "lembaga" in tables:
        op.drop_index(op.f("ix_lembaga_name"), table_name="lembaga")
        op.drop_index(op.f("ix_lembaga_id"), table_name="lembaga")
        op.drop_table("lembaga")
