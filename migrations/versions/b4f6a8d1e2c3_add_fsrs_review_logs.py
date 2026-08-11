"""Add FSRS scheduling state and review logs.

Revision ID: b4f6a8d1e2c3
Revises: 6a17c891b54e
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa


revision = "b4f6a8d1e2c3"
down_revision = "6a17c891b54e"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "user",
        sa.Column("desired_retention", sa.Float(), nullable=True, server_default="0.9"),
    )
    op.add_column(
        "card",
        sa.Column("scheduler_type", sa.String(length=30), nullable=True, server_default="sm2"),
    )
    op.add_column(
        "card",
        sa.Column("scheduler_state", sa.Text(), nullable=True, server_default=""),
    )
    op.add_column(
        "card",
        sa.Column("scheduler_version", sa.String(length=30), nullable=True, server_default="legacy"),
    )
    op.create_table(
        "review_log",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("card_id", sa.Integer(), nullable=False),
        sa.Column("rating", sa.String(length=12), nullable=False),
        sa.Column("response_time", sa.Float(), nullable=True),
        sa.Column("retrievability_before", sa.Float(), nullable=True),
        sa.Column("scheduled_days", sa.Integer(), nullable=True),
        sa.Column("scheduler_version", sa.String(length=30), nullable=True),
        sa.Column("previous_state", sa.Text(), nullable=True),
        sa.Column("review_log", sa.Text(), nullable=True),
        sa.Column("next_state", sa.Text(), nullable=True),
        sa.Column("reviewed_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["card_id"], ["card.id"]),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"]),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_review_log_user_id", "review_log", ["user_id"], unique=False)
    op.create_index("ix_review_log_card_id", "review_log", ["card_id"], unique=False)
    op.create_index("ix_review_log_reviewed_at", "review_log", ["reviewed_at"], unique=False)


def downgrade():
    op.drop_index("ix_review_log_reviewed_at", table_name="review_log")
    op.drop_index("ix_review_log_card_id", table_name="review_log")
    op.drop_index("ix_review_log_user_id", table_name="review_log")
    op.drop_table("review_log")
    op.drop_column("card", "scheduler_version")
    op.drop_column("card", "scheduler_state")
    op.drop_column("card", "scheduler_type")
    op.drop_column("user", "desired_retention")
