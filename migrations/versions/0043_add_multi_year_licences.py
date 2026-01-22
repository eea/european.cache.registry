"""empty message

Revision ID: 0043
Revises: 0042
Create Date: 2026-01-21 15:33:40.339691

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = "0043"
down_revision = "0042"
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "combined_nomenclature",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=20), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "detailed_use",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("short_code", sa.String(length=20), nullable=True),
        sa.Column("description", sa.String(length=255), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "substance_nomenclature",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("chemical_name", sa.String(length=100), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "cn_quantity",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("combined_nomenclature_id", sa.Integer(), nullable=False),
        sa.Column(
            "reserved_ods_net_mass",
            sa.Float(precision=7, asdecimal=True),
            nullable=True,
        ),
        sa.Column(
            "consumed_ods_net_mass",
            sa.Float(precision=7, asdecimal=True),
            nullable=True,
        ),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["combined_nomenclature_id"],
            ["combined_nomenclature.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "multi_year_licence",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("licence_id", sa.Integer(), nullable=True),
        sa.Column("long_licence_number", sa.String(length=50), nullable=True),
        sa.Column("status", sa.String(length=50), nullable=True),
        sa.Column("status_date", sa.Date(), nullable=True),
        sa.Column("validity_start_date", sa.Date(), nullable=True),
        sa.Column("validity_end_date", sa.Date(), nullable=True),
        sa.Column("licence_type", sa.String(length=10), nullable=True),
        sa.Column("substance_mixture", sa.String(length=20), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.Column("update_date", sa.Date(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.Column("eu_only_representative_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["eu_only_representative_id"],
            ["represent.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "multi_year_licence_combined_nomenclature_link",
        sa.Column("multi_year_licence_id", sa.Integer(), nullable=True),
        sa.Column("combined_nomenclature_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["combined_nomenclature_id"],
            ["combined_nomenclature.id"],
        ),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["multi_year_licence.id"],
        ),
    )
    op.create_table(
        "multi_year_licence_detailed_use_link",
        sa.Column("multi_year_licence_id", sa.Integer(), nullable=False),
        sa.Column("detailed_use_id", sa.Integer(), nullable=False),
        sa.Column("valid_until", sa.Date(), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["detailed_use_id"],
            ["detailed_use.id"],
        ),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["multi_year_licence.id"],
        ),
        sa.PrimaryKeyConstraint("multi_year_licence_id", "detailed_use_id"),
    )
    op.create_table(
        "multi_year_licence_substance_link",
        sa.Column("multi_year_licence_id", sa.Integer(), nullable=True),
        sa.Column("substance_nomenclature_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["multi_year_licence.id"],
        ),
        sa.ForeignKeyConstraint(
            ["substance_nomenclature_id"],
            ["substance_nomenclature.id"],
        ),
    )
    op.create_table(
        "movement_reference_number",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("undertaking_id", sa.Integer(), nullable=False),
        sa.Column("multi_year_licence_id", sa.Integer(), nullable=True),
        sa.Column("ghost_licence_number", sa.Boolean(), nullable=False),
        sa.Column("mrn", sa.String(length=32), nullable=False),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.ForeignKeyConstraint(
            ["multi_year_licence_id"],
            ["licence.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )

    with op.batch_alter_table("mail_address", schema=None) as batch_op:
        batch_op.alter_column(
            "timestamp",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )

    with op.batch_alter_table("matching_log", schema=None) as batch_op:
        batch_op.alter_column(
            "timestamp",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )

    with op.batch_alter_table("organization_log", schema=None) as batch_op:
        batch_op.alter_column(
            "execution_time",
            existing_type=postgresql.TIMESTAMP(),
            type_=sa.DateTime(timezone=True),
            existing_nullable=True,
        )


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    with op.batch_alter_table("organization_log", schema=None) as batch_op:
        batch_op.alter_column(
            "execution_time",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=True,
        )

    with op.batch_alter_table("matching_log", schema=None) as batch_op:
        batch_op.alter_column(
            "timestamp",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=True,
        )

    with op.batch_alter_table("mail_address", schema=None) as batch_op:
        batch_op.alter_column(
            "timestamp",
            existing_type=sa.DateTime(timezone=True),
            type_=postgresql.TIMESTAMP(),
            existing_nullable=True,
        )

    op.drop_table("movement_reference_number")
    op.drop_table("multi_year_licence_substance_link")
    op.drop_table("multi_year_licence_detailed_use_link")
    op.drop_table("multi_year_licence_combined_nomenclature_link")
    op.drop_table("multi_year_licence")
    op.drop_table("cn_quantity")
    op.drop_table("substance_nomenclature")
    op.drop_table("detailed_use")
    op.drop_table("combined_nomenclature")
