"""Add confidence column to projects."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0004_projects_confidence"
down_revision = "0003_requirements_conversation_turns"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Add confidence column to projects."""
    op.add_column("projects", sa.Column("confidence", sa.Float(), nullable=True))


def downgrade() -> None:
    """Remove confidence column from projects."""
    op.drop_column("projects", "confidence")
