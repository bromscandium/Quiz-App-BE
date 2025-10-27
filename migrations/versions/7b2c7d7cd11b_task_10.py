from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
import sqlmodel

revision: str = "7b2c7d7cd11b"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "users",
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("surname", sa.String(length=100), nullable=True),
        sa.Column("nickname", sa.String(length=100), nullable=False),
        sa.Column("email", sa.String(length=320), nullable=False),
        sa.Column("hashed_password", sa.String(length=1024), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_users_email"), "users", ["email"], unique=True)
    op.create_index(op.f("ix_users_id"), "users", ["id"], unique=True)
    op.create_index(op.f("ix_users_name"), "users", ["name"], unique=False)
    op.create_index(op.f("ix_users_nickname"), "users", ["nickname"], unique=True)
    op.create_index(op.f("ix_users_surname"), "users", ["surname"], unique=False)
    op.create_table(
        "companies",
        sa.Column("owner_id", sa.UUID(), nullable=False),
        sa.Column("name", sa.String(length=100), nullable=False),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("visibility", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["owner_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_companies_id"), "companies", ["id"], unique=True)
    op.create_index(
        op.f("ix_companies_owner_id"), "companies", ["owner_id"], unique=False
    )
    op.create_index(
        op.f("ix_companies_visibility"), "companies", ["visibility"], unique=False
    )
    op.create_table(
        "company_actions",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "action_type",
            sa.Enum("REQUEST", "INVITATION", name="action_type"),
            nullable=False,
        ),
        sa.Column("invited_email", sa.String(length=320), nullable=True),
        sa.Column(
            "status",
            sa.Enum("PENDING", "ACCEPTED", "CANCELLED", name="status"),
            nullable=False,
        ),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_company_actions_action_type"),
        "company_actions",
        ["action_type"],
        unique=False,
    )
    op.create_index(
        op.f("ix_company_actions_company_id"),
        "company_actions",
        ["company_id"],
        unique=False,
    )
    op.create_index(
        op.f("ix_company_actions_invited_email"),
        "company_actions",
        ["invited_email"],
        unique=True,
    )
    op.create_index(
        op.f("ix_company_actions_status"), "company_actions", ["status"], unique=False
    )
    op.create_index(
        op.f("ix_company_actions_user_id"), "company_actions", ["user_id"], unique=False
    )
    op.create_table(
        "memberships",
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.Column("company_id", sa.UUID(), nullable=False),
        sa.Column(
            "role", sa.Enum("OWNER", "ADMIN", "MEMBER", name="role"), nullable=False
        ),
        sa.Column("is_active", sa.Boolean(), nullable=False),
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["company_id"], ["companies.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        op.f("ix_memberships_company_id"), "memberships", ["company_id"], unique=False
    )
    op.create_index(op.f("ix_memberships_id"), "memberships", ["id"], unique=True)
    op.create_index(
        op.f("ix_memberships_is_active"), "memberships", ["is_active"], unique=False
    )
    op.create_index(op.f("ix_memberships_role"), "memberships", ["role"], unique=False)
    op.create_index(
        op.f("ix_memberships_user_id"), "memberships", ["user_id"], unique=False
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_memberships_user_id"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_role"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_is_active"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_id"), table_name="memberships")
    op.drop_index(op.f("ix_memberships_company_id"), table_name="memberships")
    op.drop_table("memberships")
    op.drop_index(op.f("ix_company_actions_user_id"), table_name="company_actions")
    op.drop_index(op.f("ix_company_actions_status"), table_name="company_actions")
    op.drop_index(
        op.f("ix_company_actions_invited_email"), table_name="company_actions"
    )
    op.drop_index(op.f("ix_company_actions_company_id"), table_name="company_actions")
    op.drop_index(op.f("ix_company_actions_action_type"), table_name="company_actions")
    op.drop_table("company_actions")
    op.drop_index(op.f("ix_companies_visibility"), table_name="companies")
    op.drop_index(op.f("ix_companies_owner_id"), table_name="companies")
    op.drop_index(op.f("ix_companies_id"), table_name="companies")
    op.drop_table("companies")
    op.drop_index(op.f("ix_users_surname"), table_name="users")
    op.drop_index(op.f("ix_users_nickname"), table_name="users")
    op.drop_index(op.f("ix_users_name"), table_name="users")
    op.drop_index(op.f("ix_users_id"), table_name="users")
    op.drop_index(op.f("ix_users_email"), table_name="users")
    op.drop_table("users")
