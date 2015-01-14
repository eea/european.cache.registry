revision = '35147246416c'
down_revision = '2272bad32576'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('organization_log', sa.Column('for_username', sa.Boolean(),
                                                nullable=True))


def downgrade():
    op.drop_column('organization_log', 'for_username')
