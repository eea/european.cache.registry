"""Alter detailed use table

Revision ID: 0051
Revises: 0050
Create Date: 2026-02-06 15:57:57.719570

"""

from alembic import op
import sqlalchemy as sa


revision = "0051"
down_revision = "0050"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table(
        "multi_year_licence_detailed_use_link", schema=None
    ) as batch_op:
        batch_op.drop_column("date_created")
        batch_op.drop_column("date_updated")
        batch_op.drop_column("valid_until")


def downgrade():
    with op.batch_alter_table(
        "multi_year_licence_detailed_use_link", schema=None
    ) as batch_op:
        batch_op.add_column(
            sa.Column("valid_until", sa.DATE(), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("date_updated", sa.DATE(), autoincrement=False, nullable=True)
        )
        batch_op.add_column(
            sa.Column("date_created", sa.DATE(), autoincrement=False, nullable=True)
        )
