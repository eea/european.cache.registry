revision = '0003'
down_revision = '0002'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'organization_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('update_time', sa.DateTime(), nullable=True),
        sa.Column('organizations', sa.Integer(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('organization_log')
