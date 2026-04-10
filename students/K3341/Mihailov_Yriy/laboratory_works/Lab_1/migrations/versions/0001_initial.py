"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-04-08
"""
from alembic import op
import sqlalchemy as sa


revision = "0001_initial"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    # user table
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=False),
        sa.Column("full_name", sa.String(), nullable=False),
        sa.Column("password_hash", sa.String(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("email"),
        sa.UniqueConstraint("username"),
    )
    op.create_index("ix_user_username", "user", ["username"])

    # tag table
    op.create_table(
        "tag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("color", sa.String(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("name"),
    )

    # task table
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("owner_user_id", sa.Integer(), nullable=False),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("deadline", sa.DateTime(), nullable=True),
        sa.Column("priority", sa.String(), nullable=False, server_default="medium"),
        sa.Column("status", sa.String(), nullable=False, server_default="todo"),
        sa.Column("estimated_minutes", sa.Integer(), nullable=True),
        sa.Column("recurrence_rule", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["owner_user_id"], ["user.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_task_owner_user_id", "task", ["owner_user_id"])
    op.create_index("ix_task_status", "task", ["status"])
    op.create_index("ix_task_priority", "task", ["priority"])

    # user_task_assignment
    op.create_table(
        "user_task_assignment",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("user_id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("comment", sa.String(), nullable=True),
        sa.Column("assigned_at", sa.DateTime(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["user.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("user_id", "task_id", name="uq_user_task"),
    )
    op.create_index("ix_user_task_assignment_user_id", "user_task_assignment", ["user_id"])
    op.create_index("ix_user_task_assignment_task_id", "user_task_assignment", ["task_id"])

    # task_tag
    op.create_table(
        "task_tag",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("tag_id", sa.Integer(), nullable=False),
        sa.Column("is_primary", sa.Boolean(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["tag_id"], ["tag.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("task_id", "tag_id", name="uq_task_tag"),
    )
    op.create_index("ix_task_tag_task_id", "task_tag", ["task_id"])
    op.create_index("ix_task_tag_tag_id", "task_tag", ["tag_id"])
    op.create_index("ix_task_tag_is_primary", "task_tag", ["is_primary"])


def downgrade() -> None:
    op.drop_table("task_tag")
    op.drop_table("user_task_assignment")
    op.drop_table("task")
    op.drop_table("tag")
    op.drop_index("ix_user_username", table_name="user")
    op.drop_table("user")