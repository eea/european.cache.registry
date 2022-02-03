"""empty message

Revision ID: 177d341a9c3c
Revises: 0034
Create Date: 2022-02-03 13:36:56.196359

"""
from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import DOUBLE_PRECISION
# revision identifiers, used by Alembic.
revision = '0035'
down_revision = '0034'
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=sa.Float(precision=7),
        type_=DOUBLE_PRECISION,
    )

def downgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=DOUBLE_PRECISION,
        type_=sa.Float(precision=7),
    )
