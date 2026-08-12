"""Add shared Listening stimulus playback audit data.

Revision ID: c5e8f1a2b4d6
Revises: a3c9e7b1d2f4
Create Date: 2026-08-12
"""

from alembic import op
import sqlalchemy as sa


revision = "c5e8f1a2b4d6"
down_revision = "a3c9e7b1d2f4"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column("diagnostic_attempt", sa.Column("content_version", sa.String(length=32), nullable=True))
    op.add_column("diagnostic_response", sa.Column("stimulus_id", sa.String(length=100), nullable=True))
    op.add_column("diagnostic_response", sa.Column("script_version", sa.String(length=32), nullable=True))
    op.add_column("diagnostic_response", sa.Column("audio_duration_seconds", sa.Float(), nullable=True))
    op.create_table(
        "diagnostic_stimulus_playback",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("attempt_id", sa.Integer(), sa.ForeignKey("diagnostic_attempt.id"), nullable=False),
        sa.Column("stimulus_id", sa.String(length=100), nullable=False),
        sa.Column("audio_id", sa.String(length=100), nullable=False),
        sa.Column("script_version", sa.String(length=32), nullable=False),
        sa.Column("audio_duration_seconds", sa.Float(), nullable=True),
        sa.Column("play_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("first_played_at", sa.DateTime(), nullable=True),
        sa.Column("last_played_at", sa.DateTime(), nullable=True),
        sa.UniqueConstraint("attempt_id", "stimulus_id", name="uq_diagnostic_stimulus_playback_attempt_stimulus"),
    )
    op.create_index(
        "ix_diagnostic_stimulus_playback_attempt_id",
        "diagnostic_stimulus_playback",
        ["attempt_id"],
    )


def downgrade():
    op.drop_index("ix_diagnostic_stimulus_playback_attempt_id", table_name="diagnostic_stimulus_playback")
    op.drop_table("diagnostic_stimulus_playback")
    with op.batch_alter_table("diagnostic_response") as batch_op:
        batch_op.drop_column("audio_duration_seconds")
        batch_op.drop_column("script_version")
        batch_op.drop_column("stimulus_id")
    with op.batch_alter_table("diagnostic_attempt") as batch_op:
        batch_op.drop_column("content_version")
