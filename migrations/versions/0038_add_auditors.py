"""add_auditors

Revision ID: 0038
Revises: 0037
Create Date: 2024-12-18 08:41:47.540100

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0038"
down_revision = "0037"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auditor",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("auditor_uid", sa.String(length=20), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.Column(
            "date_created_in_ecr",
            sa.Date(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
        sa.Column("date_updated_in_ecr", sa.Date(), nullable=True),
        sa.Column(
            "status",
            sa.Enum(
                "DRAFT",
                "SELF_REVISION",
                "SENT_TO_REVISION",
                "REQUESTED",
                "VALID",
                "CANCELLED",
                name="status",
            ),
            nullable=True,
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "auditor_users",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("auditor_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["auditor_id"],
            ["auditor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
    )
    usertype = sa.Enum(
        "AUDITOR_ORG_FGAS",
        "AUDITOR_ORG_AND_VERIFIER",
        "AUDITOR_ORG_ONLY_VERIFIER",
        name="usertype",
    )
    usertype.create(op.get_bind())
    op.add_column(
        "user",
        sa.Column(
            "type",
            sa.Enum(
                "AUDITOR_ORG_FGAS",
                "AUDITOR_ORG_AND_VERIFIER",
                "AUDITOR_ORG_ONLY_VERIFIER",
                name="usertype",
            ),
            nullable=True,
        ),
    )


def downgrade():
    op.drop_column("user", "type")
    usertype = sa.Enum(
        "AUDITOR_ORG_FGAS",
        "AUDITOR_ORG_AND_VERIFIER",
        "AUDITOR_ORG_ONLY_VERIFIER",
        name="usertype",
    )
    usertype.drop(op.get_bind())
    op.drop_table("auditor_users")
    op.drop_table("auditor")
