revision = '0002'
down_revision = '0001'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('undertaking', sa.Column('oldcompany_account', sa.String(length=255), nullable=True))
    op.add_column('undertaking', sa.Column('oldcompany_extid', sa.Integer(), nullable=True))
    op.add_column('undertaking', sa.Column('oldcompany_verified', sa.Boolean(), nullable=True))


def downgrade():
    op.drop_column('undertaking', 'oldcompany_verified')
    op.drop_column('undertaking', 'oldcompany_extid')
    op.drop_column('undertaking', 'oldcompany_account')
