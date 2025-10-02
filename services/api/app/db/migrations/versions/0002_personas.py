"""Create personas table."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql


revision = "0002_personas"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


PERSONA_ROLES = ("client", "lead", "developer", "pm_agent")


def upgrade() -> None:
    """Create the personas table and persona_role enum."""
    persona_role = postgresql.ENUM(*PERSONA_ROLES, name="persona_role")
    persona_role_column = postgresql.ENUM(*PERSONA_ROLES, name="persona_role", create_type=False)
    persona_role.create(op.get_bind(), checkfirst=True)

    op.create_table(
        "personas",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.Integer(), sa.ForeignKey("projects.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", sa.Integer(), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("role", persona_role_column, nullable=False),
        sa.Column("display_name", sa.String(length=255), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            server_onupdate=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
    )


def downgrade() -> None:
    """Drop the personas table and persona_role enum."""
    op.drop_table("personas")

    persona_role = postgresql.ENUM(*PERSONA_ROLES, name="persona_role")
    persona_role.drop(op.get_bind(), checkfirst=True)
