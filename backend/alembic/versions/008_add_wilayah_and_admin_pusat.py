"""add wilayah and admin pusat

Revision ID: 008
Revises: 007
Create Date: 2026-07-04
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "008"
down_revision: Union[str, None] = "007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    # 0. If using PostgreSQL, check and add 'admin_pusat' value to 'userrole' enum type
    if conn.dialect.name == "postgresql":
        try:
            result = conn.execute(sa.text(
                "SELECT 1 FROM pg_type t "
                "JOIN pg_enum e ON t.oid = e.enumtypid "
                "WHERE t.typname = 'userrole' AND e.enumlabel = 'admin_pusat'"
            )).first()
            if not result:
                op.execute("COMMIT")
                op.execute("ALTER TYPE userrole ADD VALUE 'admin_pusat'")
        except Exception:
            pass

    # 1. Create table 'wilayah'
    if "wilayah" not in tables:
        op.create_table(
            "wilayah",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("name", sa.String(length=120), nullable=False),
            sa.Column("credits", sa.Integer(), nullable=False, server_default="0"),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.PrimaryKeyConstraint("id")
        )
        op.create_index(op.f("ix_wilayah_id"), "wilayah", ["id"], unique=False)
        op.create_index(op.f("ix_wilayah_name"), "wilayah", ["name"], unique=True)

    # 2. Add columns to existing tables
    # Add wilayah_id to 'users'
    users_columns = [col["name"] for col in inspector.get_columns("users")]
    if "wilayah_id" not in users_columns:
        op.add_column("users", sa.Column("wilayah_id", sa.Integer(), sa.ForeignKey("wilayah.id"), nullable=True))

    # Add wilayah_id to 'lembaga'
    lembaga_columns = [col["name"] for col in inspector.get_columns("lembaga")]
    if "wilayah_id" not in lembaga_columns:
        op.add_column("lembaga", sa.Column("wilayah_id", sa.Integer(), sa.ForeignKey("wilayah.id"), nullable=True))

    # Add wilayah_id to 'invoices' and make 'lembaga_id' nullable
    invoices_columns = [col["name"] for col in inspector.get_columns("invoices")]
    if "wilayah_id" not in invoices_columns:
        op.add_column("invoices", sa.Column("wilayah_id", sa.Integer(), sa.ForeignKey("wilayah.id"), nullable=True))
    
    # Make lembaga_id nullable (compatible across SQLite and Postgres)
    with op.batch_alter_table("invoices") as batch_op:
        batch_op.alter_column("lembaga_id", existing_type=sa.Integer(), nullable=True)

    # Add wilayah_id to 'payment_logs' and make 'lembaga_id' nullable
    payment_logs_columns = [col["name"] for col in inspector.get_columns("payment_logs")]
    if "wilayah_id" not in payment_logs_columns:
        op.add_column("payment_logs", sa.Column("wilayah_id", sa.Integer(), sa.ForeignKey("wilayah.id"), nullable=True))

    with op.batch_alter_table("payment_logs") as batch_op:
        batch_op.alter_column("lembaga_id", existing_type=sa.Integer(), nullable=True)


def downgrade() -> None:
    # Remove columns and tables
    with op.batch_alter_table("payment_logs") as batch_op:
        batch_op.alter_column("lembaga_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("wilayah_id")

    with op.batch_alter_table("invoices") as batch_op:
        batch_op.alter_column("lembaga_id", existing_type=sa.Integer(), nullable=False)
        batch_op.drop_column("wilayah_id")

    op.drop_column("lembaga", "wilayah_id")
    op.drop_column("users", "wilayah_id")
    
    op.drop_index(op.f("ix_wilayah_name"), table_name="wilayah")
    op.drop_index(op.f("ix_wilayah_id"), table_name="wilayah")
    op.drop_table("wilayah")
