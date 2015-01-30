revision = '576264dfff3f'
down_revision = '191da78979d9'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        'mail_address',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('mail', sa.String(length=255), nullable=True),
        sa.Column('timestamp', sa.DateTime(), nullable=True),
        sa.Column('first_name', sa.String(length=255), nullable=True),
        sa.Column('last_name', sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('mail_address')
