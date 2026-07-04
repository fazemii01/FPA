"""seed admin pusat

Revision ID: 009
Revises: 008
Create Date: 2026-07-04
"""

from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa


revision: str = "009"
down_revision: Union[str, None] = "008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    conn = op.get_bind()
    
    # Seed Admin Pusat user if not exists
    from app.core.security import get_password_hash
    import datetime

    existing = conn.execute(sa.text("SELECT id FROM users WHERE email = 'pusat@alliago.id'")).first()
    if not existing:
        hashed_pw = get_password_hash("Alliapusat@1")
        conn.execute(sa.text(
            "INSERT INTO users (email, hashed_password, full_name, role, is_active, created_at, updated_at) "
            "VALUES ('pusat@alliago.id', :hp, 'Admin Pusat', 'admin_pusat', :active, :now, :now)"
        ), {"hp": hashed_pw, "active": True, "now": datetime.datetime.utcnow()})


def downgrade() -> None:
    conn = op.get_bind()
    conn.execute(sa.text("DELETE FROM users WHERE email = 'pusat@alliago.id'"))
