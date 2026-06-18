"""add invoices table

Revision ID: 005
Revises: 004
Create Date: 2026-06-17
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "005"
down_revision: Union[str, None] = "004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "invoices" not in tables:
        op.create_table(
            "invoices",
            sa.Column("id", sa.Integer(), nullable=False),
            sa.Column("uuid", sa.String(length=50), nullable=False),
            sa.Column("code", sa.String(length=20), nullable=False),
            sa.Column("lembaga_id", sa.Integer(), nullable=False),
            sa.Column("client_name", sa.String(length=120), nullable=False),
            sa.Column("description", sa.String(length=255), nullable=False),
            sa.Column("credits", sa.Integer(), nullable=False),
            sa.Column("discount", sa.Float(), nullable=False, server_default="0.0"),
            sa.Column("total_amount", sa.Float(), nullable=False),
            sa.Column("status", sa.String(length=50), nullable=False, server_default="pending"),
            sa.Column("payment_proof_path", sa.String(length=255), nullable=True),
            sa.Column("created_at", sa.DateTime(), nullable=True),
            sa.Column("updated_at", sa.DateTime(), nullable=True),
            sa.ForeignKeyConstraint(["lembaga_id"], ["lembaga.id"]),
            sa.PrimaryKeyConstraint("id"),
        )
        op.create_index(op.f("ix_invoices_id"), "invoices", ["id"], unique=False)
        op.create_index(op.f("ix_invoices_uuid"), "invoices", ["uuid"], unique=True)
        op.create_index(op.f("ix_invoices_code"), "invoices", ["code"], unique=True)


def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    tables = inspector.get_table_names()

    if "invoices" in tables:
        op.drop_table("invoices")

