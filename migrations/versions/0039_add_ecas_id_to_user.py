"""Add ecas id to user model

Revision ID: 0039
Revises: 0038
Create Date: 2025-02-11 16:43:05.923434

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0039'
down_revision = '0038'
branch_labels = None
depends_on = None


def upgrade():
    op.add_column('user', sa.Column('ecas_id', sa.String(length=255), nullable=True))

def downgrade():
    op.drop_column('user', 'ecas_id')
