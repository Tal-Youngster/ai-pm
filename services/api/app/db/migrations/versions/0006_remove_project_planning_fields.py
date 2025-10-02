"""Remove project planning fields from projects."""

from alembic import op
import sqlalchemy as sa


revision = "0006_remove_project_planning_fields"
down_revision = "0005_projects_extended_fields"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Drop planning-related columns no longer used by the application."""
    with op.batch_alter_table("projects") as batch_op:
        batch_op.drop_column("velocity")
        batch_op.drop_column("confidence")
        batch_op.drop_column("sprint_length")
        batch_op.drop_column("target_date")


def downgrade() -> None:
    """Recreate the removed planning columns."""
    with op.batch_alter_table("projects") as batch_op:
        batch_op.add_column(sa.Column("target_date", sa.Date(), nullable=True))
        batch_op.add_column(sa.Column("sprint_length", sa.Integer(), nullable=True))
        batch_op.add_column(sa.Column("confidence", sa.Float(), nullable=True))
        batch_op.add_column(sa.Column("velocity", sa.Float(), nullable=True))
