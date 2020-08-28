revision = '3f32244c7d47'
down_revision = '863b44e7b2d1'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('substance', sa.Column('s_organization_country_name', sa.String(length=100), nullable=True))

def downgrade():
    op.drop_column('substance', 's_organization_country_name')
