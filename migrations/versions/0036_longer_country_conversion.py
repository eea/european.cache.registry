"""empty message

Revision ID: ca29b6a9ac8f
Revises: 0035
Create Date: 2022-02-04 10:07:59.490487

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0036"
down_revision = "0035"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "country_codes_conversion",
        "country_code_alpha2",
        nullable=True,
        existing_type=sa.String(4),
        type_=sa.String(5),
    )


def downgrade():
    op.alter_column(
        "country_codes_conversion",
        "country_code_alpha2",
        nullable=True,
        existing_type=sa.String(5),
        type_=sa.String(4),
    )
