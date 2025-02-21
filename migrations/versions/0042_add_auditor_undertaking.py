"""Add auditor undertaking table

Revision ID: 0042
Revises: 0041
Create Date: 2025-02-20 11:48:41.925166

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0042"
down_revision = "0041"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "auditor_undertaking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("auditor_id", sa.Integer(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("start_date", sa.Date(), nullable=False),
        sa.Column("end_date", sa.Date(), nullable=True),
        sa.Column("reporting_envelope_url", sa.String(length=128), nullable=True),
        sa.Column("verification_envelope_url", sa.String(length=128), nullable=True),
        sa.ForeignKeyConstraint(
            ["auditor_id"],
            ["auditor.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("auditor_undertaking")
