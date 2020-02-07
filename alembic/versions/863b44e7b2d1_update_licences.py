revision = '863b44e7b2d1'
down_revision = 'f4be5e7999a0'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.add_column('delivery_licence', sa.Column('updated_since', sa.Date(), nullable=True))
    op.add_column('licence', sa.Column('updated_since', sa.String(length=30), nullable=True))
    op.alter_column('licence', 'qty_qdp_percentage', nullable=False,
                                existing_type=sa.Float(precision=7), new_column_name='total_odp_mass')
    op.alter_column('licence', 'qty_percentage', nullable=False,
                                existing_type=sa.String(length=30), new_column_name='net_mass')


def downgrade():
    op.alter_column('licence', 'total_odp_mass', nullable=False,
                                existing_type=sa.Float(precision=7), new_column_name='qty_qdp_percentage')
    op.alter_column('licence', 'net_mass', nullable=False,
                                existing_type=sa.String(length=30), new_column_name='qty_percentage')
    op.drop_column('licence', 'updated_since')
    op.drop_column('delivery_licence', 'updated_since')
