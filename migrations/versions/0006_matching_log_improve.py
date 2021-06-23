revision = "0006"
down_revision = "0005"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "matching_log",
        sa.Column("oldcompany_account", sa.String(length=255), nullable=True),
    )


def downgrade():
    op.drop_column("matching_log", "oldcompany_account")
