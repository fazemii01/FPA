"""add type column to lembaga

Revision ID: 006
Revises: 005
Create Date: 2026-06-22
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "006"
down_revision: Union[str, None] = "005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("lembaga")]
    if "type" not in columns:
        op.add_column("lembaga", sa.Column("type", sa.String(length=50), nullable=False, server_default="umum"))

def downgrade() -> None:
    conn = op.get_bind()
    inspector = sa.inspect(conn)
    columns = [c["name"] for c in inspector.get_columns("lembaga")]
    if "type" in columns:
        op.drop_column("lembaga", "type")
