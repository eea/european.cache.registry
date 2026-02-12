"""Add obsolete detailed uses

Revision ID: 0054
Revises: 0053
Create Date: 2026-02-11 13:41:45.197158

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0054"
down_revision = "0053"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.add_column(sa.Column("obsolete", sa.Boolean(), nullable=True))


def downgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.drop_column("obsolete")
