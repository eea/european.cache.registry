revision = '13c10878ad8a'
down_revision = '1050f0ab5f89'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql


def upgrade():
    op.add_column('organization_log', sa.Column('execution_time', sa.DateTime(),
                                                nullable=True))
    op.add_column('organization_log', sa.Column('using_last_update', sa.Date(),
                                                nullable=True))
    op.drop_column('organization_log', 'update_time')


def downgrade():
    op.add_column('organization_log', sa.Column('update_time', mysql.DATETIME(),
                                                nullable=True))
    op.drop_column('organization_log', 'using_last_update')
    op.drop_column('organization_log', 'execution_time')