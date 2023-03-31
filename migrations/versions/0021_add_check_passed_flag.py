from alembic import op
import sqlalchemy as sa

revision = "0021"
down_revision = "0020"


def upgrade():
    op.add_column("undertaking", sa.Column("check_passed", sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column("undertaking", "check_passed")
