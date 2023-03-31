from alembic import op
import sqlalchemy as sa

revision = "0015"
down_revision = "0014"


def upgrade():
    op.alter_column("address", "zipcode", type_=sa.String(64))


def downgrade():
    op.alter_column("address", "zipcode", type_=sa.String(16))
