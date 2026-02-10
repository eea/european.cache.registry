"""add new cn_quantity table

Revision ID: 0048
Revises: 0047
Create Date: 2026-01-28 14:13:17.241052

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0048"
down_revision = "0047"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "cn_quantity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("multi_year_licence_id", sa.Integer(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.Column("combined_nomenclature_id", sa.Integer(), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column(
            "aggregated_reserved_ods_net_mass",
            sa.Float(precision=7, asdecimal=True),
            nullable=True,
        ),
        sa.Column(
            "aggregated_consumed_ods_net_mass",
            sa.Float(precision=7, asdecimal=True),
            nullable=True,
        ),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["combined_nomenclature_id"],
            ["combined_nomenclature.id"],
        ),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["multi_year_licence.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("cn_quantity")
