"""Add patch_setting table

Revision ID: 0061
Revises: 0060
Create Date: 2026-11-23 12:00:00.000000

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = '0061'
down_revision = '0060'
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        'patch_setting',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=64), nullable=False),
        sa.Column('value', sa.JSON(), nullable=False),
        sa.Column('date_updated', sa.DateTime(timezone=True), nullable=True),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('name'),
    )


def downgrade():
    op.drop_table('patch_setting')
