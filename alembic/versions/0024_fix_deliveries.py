revision = '0024'
down_revision = '0023'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.drop_column('delivery_licence', 'order')
    op.drop_column('delivery_licence', 'current')
    op.drop_column('delivery_licence', 'name')
    op.add_column('substance', sa.Column('organization_country_name', sa.String(length=4), nullable=True))


def downgrade():
    op.drop_column('substance', 'organization_country_name')
    op.add_column('delivery_licence', sa.Column('name', sa.VARCHAR(length=50), autoincrement=False, nullable=True))
    op.add_column('delivery_licence', sa.Column('current', sa.BOOLEAN(), autoincrement=False, nullable=True))
    op.add_column('delivery_licence', sa.Column('order', sa.INTEGER(), autoincrement=False, nullable=True))
