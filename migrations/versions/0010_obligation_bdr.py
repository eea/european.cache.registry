from alembic import op
import sqlalchemy as sa

revision = "0010"
down_revision = "0009"


def upgrade():
    op.add_column(
        "old_company", sa.Column("obligation", sa.String(length=32), nullable=True)
    )


def downgrade():
    op.drop_column("old_company", "obligation")
