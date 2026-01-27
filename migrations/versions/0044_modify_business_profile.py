"""modify_business_profile

Revision ID: 0044
Revises: 0043
Create Date: 2026-01-23 12:20:46.442345

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0044"
down_revision = "0043"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("businessprofile", schema=None) as batch_op:
        batch_op.add_column(sa.Column("code", sa.String(length=255), nullable=True))
        batch_op.add_column(
            sa.Column("short_code", sa.String(length=16), nullable=True)
        )

    with op.batch_alter_table("cn_quantity", schema=None) as batch_op:
        batch_op.alter_column(
            "reserved_ods_net_mass",
            existing_type=sa.REAL(),
            type_=sa.Float(precision=7, asdecimal=True),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "consumed_ods_net_mass",
            existing_type=sa.REAL(),
            type_=sa.Float(precision=7, asdecimal=True),
            existing_nullable=True,
        )


def downgrade():
    with op.batch_alter_table("cn_quantity", schema=None) as batch_op:
        batch_op.alter_column(
            "consumed_ods_net_mass",
            existing_type=sa.Float(precision=7, asdecimal=True),
            type_=sa.REAL(),
            existing_nullable=True,
        )
        batch_op.alter_column(
            "reserved_ods_net_mass",
            existing_type=sa.Float(precision=7, asdecimal=True),
            type_=sa.REAL(),
            existing_nullable=True,
        )

    with op.batch_alter_table("businessprofile", schema=None) as batch_op:
        batch_op.drop_column("short_code")
        batch_op.drop_column("code")
