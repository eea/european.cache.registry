"""Add licence type to multi year aggregated

Revision ID: 0056
Revises: 0055
Create Date: 2026-02-13 11:52:58.380761

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0056"
down_revision = "0055"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("licence_type", sa.String(length=10), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.drop_column("licence_type")
