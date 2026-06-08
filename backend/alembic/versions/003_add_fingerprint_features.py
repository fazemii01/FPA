"""add fingerprint features

Revision ID: 003
Revises: 002
Create Date: 2026-05-21
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


revision: str = "003"
down_revision: Union[str, None] = "002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "fingerprint_features",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("fingerprint_id", sa.Integer(), nullable=False),
        sa.Column("scan_session_id", sa.Integer(), nullable=False),
        sa.Column("pattern_type", sa.String(length=32), nullable=False),
        sa.Column("ridge_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("ridge_density", sa.Float(), nullable=False, server_default="0"),
        sa.Column("orientation_stability", sa.Float(), nullable=False, server_default="0"),
        sa.Column("minutiae_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("core_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("delta_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("quality_score", sa.Float(), nullable=False, server_default="0"),
        sa.Column("features_json", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["fingerprint_id"], ["fingerprints.id"]),
        sa.ForeignKeyConstraint(["scan_session_id"], ["scan_sessions.id"]),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("fingerprint_id"),
    )
    op.create_index(op.f("ix_fingerprint_features_id"), "fingerprint_features", ["id"], unique=False)
    op.create_index(op.f("ix_fingerprint_features_scan_session_id"), "fingerprint_features", ["scan_session_id"], unique=False)


def downgrade() -> None:
    op.drop_index(op.f("ix_fingerprint_features_scan_session_id"), table_name="fingerprint_features")
    op.drop_index(op.f("ix_fingerprint_features_id"), table_name="fingerprint_features")
    op.drop_table("fingerprint_features")
