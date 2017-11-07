revision = '3b6b91477843'
down_revision = '36ed22543fdd'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('matching_log', sa.Column('domain', sa.String(length=32),
                  nullable=False, server_default='FGAS'))
    op.add_column('organization_log', sa.Column('domain', sa.String(length=32), 
                  nullable=False, server_default='FGAS'))


def downgrade():
    op.drop_column('organization_log', 'domain')
    op.drop_column('matching_log', 'domain')
