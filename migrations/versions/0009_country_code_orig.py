from alembic import op
import sqlalchemy as sa

revision = "0009"
down_revision = "0008"


def upgrade():
    op.add_column(
        "undertaking",
        sa.Column("country_code_orig", sa.String(length=10), default="", nullable=True),
    )


def downgrade():
    op.drop_column("undertaking", "country_code_orig")
