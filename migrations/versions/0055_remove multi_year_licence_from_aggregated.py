"""empty message

Revision ID: 0055
Revises: 0054
Create Date: 2026-02-13 10:29:25.411949

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0055"
down_revision = "0054"
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.drop_constraint(
            "multi_year_licence_aggregated_multi_year_licence_id_fkey",
            type_="foreignkey",
        )
        batch_op.drop_column("multi_year_licence_id")


def downgrade():
    with op.batch_alter_table("multi_year_licence_aggregated", schema=None) as batch_op:
        batch_op.add_column(
            sa.Column(
                "multi_year_licence_id",
                sa.INTEGER(),
                autoincrement=False,
                nullable=True,
            )
        )
        batch_op.create_foreign_key(
            "multi_year_licence_aggregated_multi_year_licence_id_fkey",
            "multi_year_licence",
            ["multi_year_licence_id"],
            ["id"],
        )
