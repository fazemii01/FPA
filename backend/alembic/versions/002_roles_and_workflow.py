"""Sprint 0: workflow-aligned roles and session lifecycle

Revision ID: 002
Revises: 001
Create Date: 2026-05-21 00:00:00.000000

Changes:
- Replace users.is_admin (bool) with users.role (enum: admin|staff)
- Add participant fields + review fields to scan_sessions
- Replace SessionStatus enum with 10-value workflow lifecycle
"""
from alembic import op
import sqlalchemy as sa


revision = "002"
down_revision = "001"
branch_labels = None
depends_on = None


OLD_STATUSES = ("IN_PROGRESS", "COMPLETED", "FAILED")
NEW_STATUSES = (
    "draft",
    "registered",
    "scanning",
    "scan_completed",
    "waiting_for_review",
    "approved",
    "rejected",
    "need_rescan",
    "generating_report",
    "report_generated",
)


def upgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # ---- users: role enum ----
    user_role = sa.Enum("admin", "staff", name="userrole")
    if dialect == "postgresql":
        user_role.create(bind, checkfirst=True)

    op.add_column(
        "users",
        sa.Column("role", user_role, nullable=False, server_default="staff"),
    )
    # Back-fill from legacy is_admin
    op.execute("UPDATE users SET role = 'admin' WHERE is_admin = TRUE")
    op.drop_column("users", "is_admin")

    # ---- scan_sessions: participant + review columns ----
    op.add_column(
        "scan_sessions",
        sa.Column("participant_name", sa.String(length=120), nullable=False, server_default=""),
    )
    op.add_column(
        "scan_sessions",
        sa.Column("participant_age", sa.Integer(), nullable=False, server_default="0"),
    )
    op.add_column(
        "scan_sessions",
        sa.Column("participant_gender", sa.String(length=16), nullable=True),
    )
    op.add_column("scan_sessions", sa.Column("notes", sa.Text(), nullable=True))
    op.add_column("scan_sessions", sa.Column("submitted_at", sa.DateTime(), nullable=True))
    op.add_column(
        "scan_sessions",
        sa.Column("reviewed_by_id", sa.Integer(), sa.ForeignKey("users.id"), nullable=True),
    )
    op.add_column("scan_sessions", sa.Column("reviewed_at", sa.DateTime(), nullable=True))
    op.add_column("scan_sessions", sa.Column("approved_at", sa.DateTime(), nullable=True))
    op.add_column("scan_sessions", sa.Column("rejection_reason", sa.Text(), nullable=True))

    # ---- scan_sessions: replace status enum ----
    if dialect == "postgresql":
        # Postgres: create new enum, swap values, drop old
        op.execute("ALTER TYPE sessionstatus RENAME TO sessionstatus_old")
        new_enum = sa.Enum(*NEW_STATUSES, name="sessionstatus")
        new_enum.create(bind, checkfirst=True)
        # Convert column via text -> new enum (with value mapping)
        op.execute("ALTER TABLE scan_sessions ALTER COLUMN status TYPE text USING status::text")
        op.execute(
            """
            UPDATE scan_sessions SET status = CASE
                WHEN status = 'IN_PROGRESS' THEN 'scanning'
                WHEN status = 'COMPLETED'   THEN 'report_generated'
                WHEN status = 'FAILED'      THEN 'rejected'
                ELSE 'draft'
            END
            """
        )
        op.execute(
            "ALTER TABLE scan_sessions ALTER COLUMN status TYPE sessionstatus USING status::sessionstatus"
        )
        op.execute("DROP TYPE sessionstatus_old")
    else:
        # SQLite or other: column is stored as text already; just rewrite values
        op.execute(
            """
            UPDATE scan_sessions SET status = CASE
                WHEN status = 'IN_PROGRESS' THEN 'scanning'
                WHEN status = 'COMPLETED'   THEN 'report_generated'
                WHEN status = 'FAILED'      THEN 'rejected'
                ELSE 'draft'
            END
            """
        )


def downgrade() -> None:
    bind = op.get_bind()
    dialect = bind.dialect.name

    # ---- scan_sessions: revert status enum ----
    if dialect == "postgresql":
        op.execute("ALTER TYPE sessionstatus RENAME TO sessionstatus_new")
        old_enum = sa.Enum(*OLD_STATUSES, name="sessionstatus")
        old_enum.create(bind, checkfirst=True)
        op.execute("ALTER TABLE scan_sessions ALTER COLUMN status TYPE text USING status::text")
        op.execute(
            """
            UPDATE scan_sessions SET status = CASE
                WHEN status IN ('scanning','draft','registered','scan_completed','waiting_for_review','need_rescan','generating_report','approved') THEN 'IN_PROGRESS'
                WHEN status = 'report_generated' THEN 'COMPLETED'
                ELSE 'FAILED'
            END
            """
        )
        op.execute(
            "ALTER TABLE scan_sessions ALTER COLUMN status TYPE sessionstatus USING status::sessionstatus"
        )
        op.execute("DROP TYPE sessionstatus_new")

    op.drop_column("scan_sessions", "rejection_reason")
    op.drop_column("scan_sessions", "approved_at")
    op.drop_column("scan_sessions", "reviewed_at")
    op.drop_column("scan_sessions", "reviewed_by_id")
    op.drop_column("scan_sessions", "submitted_at")
    op.drop_column("scan_sessions", "notes")
    op.drop_column("scan_sessions", "participant_gender")
    op.drop_column("scan_sessions", "participant_age")
    op.drop_column("scan_sessions", "participant_name")

    op.add_column("users", sa.Column("is_admin", sa.Boolean(), nullable=True, server_default=sa.false()))
    op.execute("UPDATE users SET is_admin = TRUE WHERE role = 'admin'")
    op.drop_column("users", "role")
    if dialect == "postgresql":
        sa.Enum(name="userrole").drop(bind, checkfirst=True)
