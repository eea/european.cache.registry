from alembic import op
import sqlalchemy as sa

revision = "0007"
down_revision = "0006"


def upgrade():
    op.add_column("old_company", sa.Column("valid", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("old_company", "valid")
