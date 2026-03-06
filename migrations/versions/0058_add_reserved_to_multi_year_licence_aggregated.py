"""Add reserved and quantity to multi_year_licence_aggregated

Revision ID:0058
Revises: 0057
Create Date: 2026-03-06 11:42:28.832371

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0058"
down_revision = "0057"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.add_column(sa.Column("quantity", sa.Float(precision=7), nullable=True))
        batch_op.add_column(sa.Column("reserved", sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.drop_column("reserved")
        batch_op.drop_column("quantity")
