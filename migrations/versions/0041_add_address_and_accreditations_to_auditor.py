"""Add address and accreditations to auditor table

Revision ID: 0041
Revises: 0040
Create Date: 2025-02-19 10:22:03.719989

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0041"
down_revision = "0040"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auditor_ms_accreditation_issuing_countries",
        sa.Column("country_id", sa.Integer(), nullable=False),
        sa.Column("auditor_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["auditor_id"],
            ["auditor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["country.id"],
        ),
    )
    op.add_column("auditor", sa.Column("address_id", sa.Integer(), nullable=False))
    op.add_column("auditor", sa.Column("website", sa.String(length=255), nullable=True))
    op.add_column("auditor", sa.Column("phone", sa.String(length=32), nullable=False))
    op.add_column(
        "auditor", sa.Column("ets_accreditation", sa.Boolean(), nullable=False)
    )
    op.add_column(
        "auditor", sa.Column("ms_accreditation", sa.Boolean(), nullable=False)
    )
    op.alter_column(
        "auditor", "auditor_uid", existing_type=sa.VARCHAR(length=20), nullable=False
    )
    op.alter_column(
        "auditor", "name", existing_type=sa.VARCHAR(length=255), nullable=False
    )
    op.alter_column("auditor", "date_created", existing_type=sa.DATE(), nullable=False)
    op.alter_column("auditor", "date_updated", existing_type=sa.DATE(), nullable=False)
    op.alter_column(
        "auditor",
        "date_created_in_ecr",
        existing_type=sa.DATE(),
        nullable=False,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column(
        "auditor",
        "status",
        existing_type=postgresql.ENUM(
            "DRAFT",
            "SELF_REVISION",
            "SENT_TO_REVISION",
            "REQUESTED",
            "VALID",
            "CANCELLED",
            name="status",
        ),
        nullable=False,
    )
    op.create_foreign_key(
        "auditor_address_id_fkey", "auditor", "address", ["address_id"], ["id"]
    )
    op.drop_constraint(
        "auditor_users_user_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.drop_constraint(
        "auditor_users_auditor_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.create_foreign_key(
        "auditor_users_user_id_fkey", "auditor_users", "user", ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "auditor_users_auditor_id_fkey",
        "auditor_users",
        "auditor",
        ["auditor_id"],
        ["id"],
    )
    op.alter_column(
        "undertaking_users", "user_id", existing_type=sa.INTEGER(), nullable=False
    )
    op.alter_column(
        "undertaking_users",
        "undertaking_id",
        existing_type=sa.INTEGER(),
        nullable=False,
    )


def downgrade():
    op.alter_column(
        "undertaking_users", "undertaking_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.alter_column(
        "undertaking_users", "user_id", existing_type=sa.INTEGER(), nullable=True
    )
    op.drop_constraint(
        "auditor_users_auditor_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.drop_constraint(
        "auditor_users_user_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.create_foreign_key(
        "auditor_users_auditor_id_fkey",
        "auditor_users",
        "auditor",
        ["auditor_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.create_foreign_key(
        "auditor_users_user_id_fkey",
        "auditor_users",
        "user",
        ["user_id"],
        ["id"],
        ondelete="CASCADE",
    )
    op.alter_column(
        "auditor",
        "status",
        existing_type=postgresql.ENUM(
            "DRAFT",
            "SELF_REVISION",
            "SENT_TO_REVISION",
            "REQUESTED",
            "VALID",
            "CANCELLED",
            name="status",
        ),
        nullable=True,
    )
    op.alter_column(
        "auditor",
        "date_created_in_ecr",
        existing_type=sa.DATE(),
        nullable=True,
        existing_server_default=sa.text("now()"),
    )
    op.alter_column("auditor", "date_updated", existing_type=sa.DATE(), nullable=True)
    op.alter_column("auditor", "date_created", existing_type=sa.DATE(), nullable=True)
    op.alter_column(
        "auditor", "name", existing_type=sa.VARCHAR(length=255), nullable=True
    )
    op.alter_column(
        "auditor", "auditor_uid", existing_type=sa.VARCHAR(length=20), nullable=True
    )
    op.drop_column("auditor", "ms_accreditation")
    op.drop_column("auditor", "ets_accreditation")
    op.drop_column("auditor", "phone")
    op.drop_column("auditor", "website")
    op.drop_column("auditor", "address_id")
    op.drop_table("auditor_ms_accreditation_issuing_countries")
