revision = '191da78979d9'
down_revision = '17c676b14273'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('old_company',
                  sa.Column('obligation', sa.String(length=32), nullable=True))


def downgrade():
    op.drop_column('old_company', 'obligation')
