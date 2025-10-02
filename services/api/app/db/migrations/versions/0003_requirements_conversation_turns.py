"""Add requirements and conversation_turns tables."""

from __future__ import annotations

import sqlalchemy as sa
from alembic import op
from pgvector.sqlalchemy import Vector
from sqlalchemy.dialects import postgresql


revision = "0003_requirements_conversation_turns"
down_revision = "0002_personas"
branch_labels = None
depends_on = None


def upgrade() -> None:
    """Create requirements and conversation turn tables."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")

    requirement_type = postgresql.ENUM(
        "feature",
        "bug",
        "improvement",
        "constraint",
        name="requirement_type",
    )
    requirement_type.create(op.get_bind(), checkfirst=True)
    requirement_type_column = postgresql.ENUM(
        "feature",
        "bug",
        "improvement",
        "constraint",
        name="requirement_type",
        create_type=False,
    )

    op.create_table(
        "requirements",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("persona_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("type", requirement_type_column, nullable=False),
        sa.Column("confidence", sa.Float(), nullable=True),
        sa.Column("cluster_id", postgresql.UUID(as_uuid=True), nullable=True),
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
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["persona_id"], ["personas.id"], ondelete="CASCADE"),
    )

    op.create_table(
        "conversation_turns",
        sa.Column("id", postgresql.UUID(as_uuid=True), primary_key=True),
        sa.Column("project_id", sa.Integer(), nullable=False),
        sa.Column("persona_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("text", sa.Text(), nullable=False),
        sa.Column("embedding", Vector(), nullable=False),
        sa.Column(
            "created_at",
            sa.DateTime(timezone=True),
            server_default=sa.text("CURRENT_TIMESTAMP"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(["project_id"], ["projects.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["persona_id"], ["personas.id"], ondelete="CASCADE"),
    )


def downgrade() -> None:
    """Drop requirements and conversation turn tables."""
    op.drop_table("conversation_turns")
    op.drop_table("requirements")

    requirement_type = postgresql.ENUM(
        "feature",
        "bug",
        "improvement",
        "constraint",
        name="requirement_type",
    )
    requirement_type.drop(op.get_bind(), checkfirst=True)
