"""Add precise FSRS intervals in minutes.

Revision ID: d3f8a1b2c4d5
Revises: c9e7d2f4a5b6
Create Date: 2026-08-11
"""

from alembic import op
import sqlalchemy as sa


revision = "d3f8a1b2c4d5"
down_revision = "c9e7d2f4a5b6"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("card", sa.Column("interval_minutes", sa.Integer(), nullable=True))
    op.add_column("review_log", sa.Column("scheduled_minutes", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("review_log", "scheduled_minutes")
    op.drop_column("card", "interval_minutes")
