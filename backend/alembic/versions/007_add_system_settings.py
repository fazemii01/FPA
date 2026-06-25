"""add system settings table

Revision ID: 007
Revises: 006
Create Date: 2026-06-25
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

revision: str = "007"
down_revision: Union[str, None] = "006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None

def upgrade() -> None:
    # Create system_settings table
    op.create_table(
        "system_settings",
        sa.Column("key", sa.String(length=100), nullable=False),
        sa.Column("value", sa.String(length=255), nullable=False),
        sa.PrimaryKeyConstraint("key")
    )
    op.create_index(op.f("ix_system_settings_key"), "system_settings", ["key"], unique=False)

    # Insert default values
    op.execute("INSERT INTO system_settings (key, value) VALUES ('topup_bulk_options', '5,10,15,20')")
    op.execute("INSERT INTO system_settings (key, value) VALUES ('price_umum', '125000')")
    op.execute("INSERT INTO system_settings (key, value) VALUES ('price_partner', '95000')")

def downgrade() -> None:
    op.drop_index(op.f("ix_system_settings_key"), table_name="system_settings")
    op.drop_table("system_settings")
