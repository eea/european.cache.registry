"""empty message

Revision ID: 88562db85f55
Revises: 0033
Create Date: 2022-01-05 10:30:00.619152

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0034"
down_revision = "0033"
branch_labels = None
depends_on = None


def upgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=sa.Integer(),
        type_=sa.Float(precision=7),
    )


def downgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=sa.Float(precision=7),
        type_=sa.Integer(),
    )
