"""Add per-domain adaptive learning profiles.

Revision ID: e4a9b2c7d6f1
Revises: d3f8a1b2c4d5
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa


revision = "e4a9b2c7d6f1"
down_revision = "d3f8a1b2c4d5"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("card", sa.Column("learning_domain", sa.String(length=50), nullable=True))
    op.create_table(
        "adaptive_learning_profile",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("user.id"), nullable=False),
        sa.Column("domain", sa.String(length=50), nullable=False),
        sa.Column("desired_retention", sa.Float(), nullable=False, server_default="0.9"),
        sa.Column("created_at", sa.DateTime(), nullable=True),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("user_id", "domain", name="uq_adaptive_profile_user_domain"),
    )
    op.create_index("ix_adaptive_learning_profile_user_id", "adaptive_learning_profile", ["user_id"])


def downgrade():
    op.drop_index("ix_adaptive_learning_profile_user_id", table_name="adaptive_learning_profile")
    op.drop_table("adaptive_learning_profile")
    op.drop_column("card", "learning_domain")
