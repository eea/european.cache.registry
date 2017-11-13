revision = 'beba44b3efb'
down_revision = '32903473e4ba'

from alembic import op
import sqlalchemy as sa

from cache_registry.models import db


def upgrade():
    op.drop_constraint('email', 'user', type_='unique')


def downgrade():
    op.create_unique_constraint(u'email', 'user', ['email'])
