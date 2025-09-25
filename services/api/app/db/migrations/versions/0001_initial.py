"""Initial empty migration."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Initial upgrade step."""


def downgrade() -> None:
    """Initial downgrade step."""
