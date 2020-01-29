revision = 'f4be5e7999a0'
down_revision = 'c5caf76d813b'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('hash_licences_json',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('hash_value', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('hash_licences_json')