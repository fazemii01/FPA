"""add available_at and report delay settings

Revision ID: 010
Revises: 009
Create Date: 2026-08-19
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "010"
down_revision: Union[str, None] = "009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # 1. Add available_at to scan_sessions
    op.add_column("scan_sessions", sa.Column("available_at", sa.DateTime(), nullable=True))

    # 2. Seed default system settings
    conn = op.get_bind()
    for key, val in [("report_delay_enabled", "false"), ("report_delay_minutes", "15")]:
        existing = conn.execute(sa.text("SELECT key FROM system_settings WHERE key = :k"), {"k": key}).first()
        if not existing:
            conn.execute(sa.text("INSERT INTO system_settings (key, value) VALUES (:k, :v)"), {"k": key, "v": val})


def downgrade() -> None:
    op.drop_column("scan_sessions", "available_at")
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM system_settings WHERE key IN ('report_delay_enabled', 'report_delay_minutes')"))
