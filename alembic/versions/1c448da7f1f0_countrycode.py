revision = '1c448da7f1f0'
down_revision = '109b94c0bb69'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('undertaking',
                  sa.Column('country_code', sa.String(length=10),
                            nullable=True))


def downgrade():
    op.drop_column('undertaking', 'country_code')
