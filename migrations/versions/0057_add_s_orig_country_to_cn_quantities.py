"""Add s_orig_country_name to cn_quantity

Revision ID: 0057
Revises: 0056
Create Date: 2026-02-26 14:31:57.762632

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0057'
down_revision = '0056'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('cn_quantity', schema=None) as batch_op:
        batch_op.add_column(sa.Column('s_orig_country_name', sa.String(length=255), nullable=True))



def downgrade():
    with op.batch_alter_table('cn_quantity', schema=None) as batch_op:
        batch_op.drop_column('s_orig_country_name')
