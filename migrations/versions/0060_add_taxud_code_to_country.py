"""Add taxud_code to country

Revision ID: 0060
Revises: 0059
Create Date: 2026-11-17 10:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0060'
down_revision = '0059'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('country', schema=None) as batch_op:
        batch_op.add_column(sa.Column('taxud_code', sa.String(length=64), nullable=True))


def downgrade():
    with op.batch_alter_table('country', schema=None) as batch_op:
        batch_op.drop_column('taxud_code')
