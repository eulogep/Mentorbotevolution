"""Add multi-domain learning path metadata.

Revision ID: c9e7d2f4a5b6
Revises: b4f6a8d1e2c3
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa


revision = "c9e7d2f4a5b6"
down_revision = "b4f6a8d1e2c3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("subject", sa.Column("domain", sa.String(length=50), nullable=True, server_default="general"))
    op.add_column("subject", sa.Column("objective_type", sa.String(length=50), nullable=True, server_default="competency"))
    op.add_column("subject", sa.Column("objective_label", sa.String(length=200), nullable=True, server_default="Compétence visée"))
    op.add_column("subject", sa.Column("target_date", sa.Date(), nullable=True))
    op.add_column("subject", sa.Column("weekly_hours", sa.Float(), nullable=True))
    op.add_column("subject", sa.Column("source", sa.String(length=50), nullable=True, server_default="user_created"))
    op.add_column("concept", sa.Column("competency_type", sa.String(length=50), nullable=True, server_default="knowledge"))
    op.add_column("concept", sa.Column("evidence_criterion", sa.Text(), nullable=True, server_default=""))


def downgrade():
    op.drop_column("concept", "evidence_criterion")
    op.drop_column("concept", "competency_type")
    op.drop_column("subject", "source")
    op.drop_column("subject", "weekly_hours")
    op.drop_column("subject", "target_date")
    op.drop_column("subject", "objective_label")
    op.drop_column("subject", "objective_type")
    op.drop_column("subject", "domain")
