revision = "0027"
down_revision = "0026"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column(
        "substance",
        sa.Column("s_organization_country_name", sa.String(length=100), nullable=True),
    )


def downgrade():
    op.drop_column("substance", "s_organization_country_name")
