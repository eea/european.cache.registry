"""empty message

Revision ID: 9954f63dad8b
Revises: 0036
Create Date: 2022-03-10 11:08:41.506148

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0037"
down_revision = "0036"
branch_labels = None
depends_on = None


def upgrade():
    op.add_column(
        "undertaking", sa.Column("eori_number", sa.String(length=255), nullable=True)
    )


def downgrade():
    op.drop_column("undertaking", "eori_number")
