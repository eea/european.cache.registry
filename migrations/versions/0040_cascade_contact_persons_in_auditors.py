"""Update cascade parameter for contact_persons relationship in auditors

Revision ID: 0040
Revises: 0039
Create Date: 2025-02-19 10:08:22.616352

"""

from alembic import op
import sqlalchemy as sa


revision = "0040"
down_revision = "0039"
branch_labels = None
depends_on = None


def upgrade():
    op.drop_constraint(
        "auditor_users_user_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.drop_constraint(
        "auditor_users_auditor_id_fkey", "auditor_users", type_="foreignkey"
    )
    op.create_foreign_key(
        None, "auditor_users", "user", ["user_id"], ["id"], ondelete="CASCADE"
    )
    op.create_foreign_key(
        None, "auditor_users", "auditor", ["auditor_id"], ["id"], ondelete="CASCADE"
    )


def downgrade():
    op.drop_constraint(None, "auditor_users", type_="foreignkey")
    op.drop_constraint(None, "auditor_users", type_="foreignkey")
    op.create_foreign_key(
        "auditor_users_user_id_fkey", "auditor_users", "user", ["user_id"], ["id"]
    )
    op.create_foreign_key(
        "auditor_users_auditor_id_fkey",
        "auditor_users",
        "auditor",
        ["auditor_id"],
        ["id"],
    )
