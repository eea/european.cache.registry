"""Add customs_procedure to cn_quantity

Revision ID: 0052
Revises: 0051
Create Date: 2026-02-09 13:42:40.556785

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0052"
down_revision = "0051"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("cn_quantity", schema=None) as batch_op:
        batch_op.add_column(sa.Column("customs_procedure", sa.Integer(), nullable=True))


def downgrade():
    with op.batch_alter_table("cn_quantity", schema=None) as batch_op:
        batch_op.drop_column("customs_procedure")
