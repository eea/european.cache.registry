"""modify detailed use

Revision ID: 0046
Revises: 0045
Create Date: 2026-01-27 09:45:59.797606

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0046"
down_revision = "0045"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.add_column(sa.Column("code", sa.String(length=255), nullable=True))
        batch_op.drop_column("description")


def downgrade():
    with op.batch_alter_table("detailed_use", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "description",
                sa.VARCHAR(length=255),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.drop_column("code")
