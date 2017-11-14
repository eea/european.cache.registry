revision = '1650a3339d15'
down_revision = '52decb727dcb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('address', 'zipcode', type_=sa.String(64))


def downgrade():
    op.alter_column('address', 'zipcode', type_=sa.String(16))
