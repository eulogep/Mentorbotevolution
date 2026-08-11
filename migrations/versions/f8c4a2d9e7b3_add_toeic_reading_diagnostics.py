"""Add original TOEIC reading diagnostic attempts and responses.

Revision ID: f8c4a2d9e7b3
Revises: e4a9b2c7d6f1
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "f8c4a2d9e7b3"
down_revision = "e4a9b2c7d6f1"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "diagnostic_attempt",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("subject_id", sa.Integer(), sa.ForeignKey("subject.id"), nullable=True),
        sa.Column("diagnostic_id", sa.String(length=100), nullable=False),
        sa.Column("status", sa.String(length=20), nullable=False, server_default="in_progress"),
        sa.Column("total_items", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("correct_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("duration_seconds", sa.Float(), nullable=True),
        sa.Column("started_at", sa.DateTime(), nullable=False),
        sa.Column("completed_at", sa.DateTime(), nullable=True),
    )
    op.create_index("ix_diagnostic_attempt_user_id", "diagnostic_attempt", ["user_id"])
    op.create_index("ix_diagnostic_attempt_subject_id", "diagnostic_attempt", ["subject_id"])
    op.create_index("ix_diagnostic_attempt_diagnostic_id", "diagnostic_attempt", ["diagnostic_id"])

    op.create_table(
        "diagnostic_response",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("diagnostic_attempt.id"), nullable=False),
        sa.Column("item_id", sa.String(length=100), nullable=False),
        sa.Column("task_type", sa.String(length=50), nullable=False),
        sa.Column("target", sa.String(length=50), nullable=False),
        sa.Column("scenario", sa.String(length=100), nullable=False),
        sa.Column("selected_index", sa.Integer(), nullable=True),
        sa.Column("is_correct", sa.Boolean(), nullable=False),
        sa.Column("response_time_seconds", sa.Float(), nullable=True),
        sa.Column("confidence", sa.Integer(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
    )
    op.create_index("ix_diagnostic_response_attempt_id", "diagnostic_response", ["attempt_id"])
    op.create_index("ix_diagnostic_response_target", "diagnostic_response", ["target"])


def downgrade():
    op.drop_index("ix_diagnostic_response_target", table_name="diagnostic_response")
    op.drop_index("ix_diagnostic_response_attempt_id", table_name="diagnostic_response")
    op.drop_table("diagnostic_response")
    op.drop_index("ix_diagnostic_attempt_diagnostic_id", table_name="diagnostic_attempt")
    op.drop_index("ix_diagnostic_attempt_subject_id", table_name="diagnostic_attempt")
    op.drop_index("ix_diagnostic_attempt_user_id", table_name="diagnostic_attempt")
    op.drop_table("diagnostic_attempt")
