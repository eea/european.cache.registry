revision = '17c676b14273'
down_revision = '1c448da7f1f0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('undertaking',
                  sa.Column('country_code_orig', sa.String(length=10),
                            default="", nullable=True))


def downgrade():
    op.drop_column('undertaking', 'country_code_orig')
