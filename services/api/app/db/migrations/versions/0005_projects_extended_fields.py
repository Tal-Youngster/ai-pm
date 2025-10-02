"""Add extended fields to projects for lifecycle management."""

from __future__ import annotations

from alembic import op
import sqlalchemy as sa


revision = "0005_projects_extended_fields"
down_revision = "0004_projects_confidence"
branch_labels = None
depends_on = None

project_status_enum = sa.Enum(
    "planned",
    "active",
    "paused",
    "completed",
    "archived",
    name="project_status",
)


def upgrade() -> None:
    """Add new metadata columns and status enum to projects."""
    bind = op.get_bind()
    project_status_enum.create(bind, checkfirst=True)

    op.add_column("projects", sa.Column("description", sa.Text(), nullable=True))
    op.add_column("projects", sa.Column("velocity", sa.Float(), nullable=True))
    op.add_column("projects", sa.Column("sprint_length", sa.Integer(), nullable=True))
    op.add_column(
        "projects",
        sa.Column("status", project_status_enum, nullable=False, server_default="active"),
    )
    op.add_column("projects", sa.Column("target_date", sa.Date(), nullable=True))


def downgrade() -> None:
    """Remove metadata columns and status enum from projects."""
    op.drop_column("projects", "target_date")
    op.drop_column("projects", "status")
    op.drop_column("projects", "sprint_length")
    op.drop_column("projects", "velocity")
    op.drop_column("projects", "description")

    bind = op.get_bind()
    project_status_enum.drop(bind, checkfirst=True)
