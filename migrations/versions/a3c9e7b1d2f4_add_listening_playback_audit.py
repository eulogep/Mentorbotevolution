"""Add auditable playback metadata to original listening responses.

Revision ID: a3c9e7b1d2f4
Revises: f8c4a2d9e7b3
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "a3c9e7b1d2f4"
down_revision = "f8c4a2d9e7b3"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("diagnostic_response", sa.Column("audio_id", sa.String(length=100), nullable=True))
    op.add_column("diagnostic_response", sa.Column("play_count", sa.Integer(), nullable=True))


def downgrade():
    op.drop_column("diagnostic_response", "play_count")
    op.drop_column("diagnostic_response", "audio_id")
