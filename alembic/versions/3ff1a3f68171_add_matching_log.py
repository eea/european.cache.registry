revision = '3ff1a3f68171'
down_revision = '13c10878ad8a'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'matching_log',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('user', sa.String(length=255), nullable=True),
        sa.Column('company_id', sa.Integer(), nullable=True),
        sa.Column('oldcompany_id', sa.Integer(), nullable=True),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('matching_log')