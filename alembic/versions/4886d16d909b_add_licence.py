revision = '4886d16d909b'
down_revision = 'b1da65cc5a22'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('history_licence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('date_created', sa.Date(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_updated', sa.Date(), nullable=True),
        sa.Column('undertaking_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['undertaking_id'], ['undertaking.id'], ),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('licence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('date_created', sa.Date(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_updated', sa.Date(), nullable=True),
        sa.Column('licence_id', sa.Integer(), nullable=True),
        sa.Column('chemical_name', sa.String(length=100), nullable=True),
        sa.Column('custom_procedure_name', sa.String(length=100), nullable=True),
        sa.Column('international_party_country_name', sa.String(length=100), nullable=True),
        sa.Column('qty_qdp_percentage', sa.String(length=50), nullable=True),
        sa.Column('qty_percentage', sa.String(length=50), nullable=True),
        sa.Column('licence_state', sa.String(length=50), nullable=True),
        sa.Column('long_licence_number', sa.String(length=50), nullable=True),
        sa.Column('template_detailed_use_code', sa.String(length=255), nullable=True),
        sa.Column('licence_type', sa.String(length=50), nullable=True),
        sa.Column('mixture_nature_type', sa.String(length=50), nullable=True),
        sa.Column('undertaking_id', sa.Integer(), nullable=True),
        sa.Column('history_licence_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['history_licence_id'], ['history_licence.id'], ),
        sa.ForeignKeyConstraint(['undertaking_id'], ['undertaking.id'], ),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('licence')
    op.drop_table('history_licence')
