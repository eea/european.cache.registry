"""Alter detailed use table

Revision ID: 0050
Revises: 0049
Create Date: 2026-02-05 12:23:51.555906

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0050"
down_revision = "0049"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("lic_use_desc", sa.String(length=255), nullable=True)
        )
        batch_op.add_column(sa.Column("lic_type", sa.String(length=50), nullable=True))


def downgrade():

    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.drop_column("lic_type")
        batch_op.drop_column("lic_use_desc")
