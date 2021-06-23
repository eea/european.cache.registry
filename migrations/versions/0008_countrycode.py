revision = "0008"
down_revision = "0007"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "undertaking",
        sa.Column("country_code", sa.String(length=10), nullable=True, default=""),
    )


def downgrade():
    op.drop_column("undertaking", "country_code")
