revision = '0317110d3c49'
down_revision = 'b1da65cc5a22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('undertaking', sa.Column('date_created_in_ecr', sa.Date(), server_default=sa.text('now()'), nullable=True))
    op.add_column('undertaking', sa.Column('date_updated_in_ecr', sa.Date(), nullable=True))

def downgrade():
    op.drop_column('undertaking', 'date_updated_in_ecr')
    op.drop_column('undertaking', 'date_created_in_ecr')
