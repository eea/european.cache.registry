"""drop cn quantity and movement reference number

Revision ID: 0047
Revises: 0046
Create Date: 2026-01-28 13:57:50.643913

"""

from alembic import op
import sqlalchemy as sa


revision = "0047"
down_revision = "0046"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_table("cn_quantity")
    op.drop_table("movement_reference_number")


def downgrade():
    op.create_table(
        "movement_reference_number",
        sa.Column(
            "id",
            sa.INTEGER(),
            server_default=sa.text(
                "nextval('movement_reference_number_id_seq'::regclass)"
            ),
            autoincrement=True,
            nullable=False,
        ),
        sa.Column("undertaking_id", sa.INTEGER(), autoincrement=False, nullable=False),
        sa.Column(
            "multi_year_licence_id", sa.INTEGER(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "ghost_licence_number", sa.BOOLEAN(), autoincrement=False, nullable=False
        ),
        sa.Column("mrn", sa.VARCHAR(length=32), autoincrement=False, nullable=False),
        sa.Column("date_created", sa.DATE(), autoincrement=False, nullable=True),
        sa.Column("date_updated", sa.DATE(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["multi_year_licence.id"],
            name="movement_reference_number_multi_year_licence_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
            name="movement_reference_number_undertaking_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="movement_reference_number_pkey"),
        postgresql_ignore_search_path=False,
    )
    op.create_table(
        "cn_quantity",
        sa.Column("id", sa.INTEGER(), autoincrement=True, nullable=False),
        sa.Column(
            "combined_nomenclature_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "movement_reference_number_id",
            sa.INTEGER(),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "reserved_ods_net_mass", sa.REAL(), autoincrement=False, nullable=True
        ),
        sa.Column(
            "consumed_ods_net_mass", sa.REAL(), autoincrement=False, nullable=True
        ),
        sa.Column("date_created", sa.DATE(), autoincrement=False, nullable=True),
        sa.Column("date_updated", sa.DATE(), autoincrement=False, nullable=True),
        sa.ForeignKeyConstraint(
            ["combined_nomenclature_id"],
            ["combined_nomenclature.id"],
            name="cn_quantity_combined_nomenclature_id_fkey",
        ),
        sa.ForeignKeyConstraint(
            ["movement_reference_number_id"],
            ["movement_reference_number.id"],
            name="cn_quantity_movement_reference_number_id_fkey",
        ),
        sa.PrimaryKeyConstraint("id", name="cn_quantity_pkey"),
    )
