"""Add licence type to detailed uses

Revision ID: 0053
Revises: 0052
Create Date: 2026-02-10 10:09:28.507864

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0053"
down_revision = "0052"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column("licence_type", sa.String(length=10), nullable=True)
        )


def downgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.drop_column("licence_type")
