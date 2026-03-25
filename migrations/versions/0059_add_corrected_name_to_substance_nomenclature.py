"""Add corrected_name to substance_nomenclature

Revision ID: 0059
Revises: 0058
Create Date: 2026-03-25 09:45:38.178278

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0059'
down_revision = '0058'
branch_labels = None
depends_on = None


def upgrade():
    with op.batch_alter_table('substance_nomenclature', schema=None) as batch_op:
        batch_op.add_column(sa.Column('corrected_name', sa.String(length=255), nullable=True))


def downgrade():
    with op.batch_alter_table('substance_nomenclature', schema=None) as batch_op:
        batch_op.drop_column('corrected_name')