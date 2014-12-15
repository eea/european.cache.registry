revision = '109b94c0bb69'
down_revision = '2272bad32576'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('old_company',
                  sa.Column('valid', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('old_company', 'valid')
