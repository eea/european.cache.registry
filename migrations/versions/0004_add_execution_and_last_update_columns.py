from alembic import op
import sqlalchemy as sa

revision = "0004"
down_revision = "0003"


def upgrade():
    op.add_column(
        "organization_log", sa.Column("execution_time", sa.DateTime(), nullable=True)
    )
    op.add_column(
        "organization_log", sa.Column("using_last_update", sa.Date(), nullable=True)
    )
    op.drop_column("organization_log", "update_time")


def downgrade():
    op.add_column(
        "organization_log", sa.Column("update_time", sa.DateTime(), nullable=True)
    )
    op.drop_column("organization_log", "using_last_update")
    op.drop_column("organization_log", "execution_time")
