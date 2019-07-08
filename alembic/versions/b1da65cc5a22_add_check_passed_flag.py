revision = 'b1da65cc5a22'
down_revision = 'd411496edccc'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('undertaking', sa.Column('check_passed', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('undertaking', 'check_passed')
