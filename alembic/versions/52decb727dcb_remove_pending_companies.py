revision = '52decb727dcb'
down_revision = 'beba44b3efb'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_table('old_company')
    op.drop_table('old_company_link')

def downgrade():
    pass
