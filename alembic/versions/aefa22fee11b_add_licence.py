revision = 'aefa22fee11b'
down_revision = '0317110d3c49'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('country_codes_conversion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('country_name_short_en', sa.String(length=100), nullable=True),
        sa.Column('country_code_alpha2', sa.String(length=4), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('licence_details_conversion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('template_detailed_use_code', sa.String(length=250), nullable=True),
        sa.Column('lic_use_kind', sa.String(length=100), nullable=True),
        sa.Column('lic_use_desc', sa.String(length=100), nullable=True),
        sa.Column('lic_type', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('substance_name_conversion',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ec_substance_name', sa.String(length=100), nullable=True),
        sa.Column('corrected_name', sa.String(length=100), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('delivery_licence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('order', sa.Integer(), nullable=True),
        sa.Column('current', sa.Boolean(), nullable=True),
        sa.Column('name', sa.String(length=50), nullable=True),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('date_created', sa.Date(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_updated', sa.Date(), nullable=True),
        sa.Column('undertaking_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['undertaking_id'], ['undertaking.id'], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('substance',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('substance', sa.String(length=100), nullable=True),
        sa.Column('lic_use_kind', sa.String(length=100), nullable=True),
        sa.Column('lic_use_desc', sa.String(length=100), nullable=True),
        sa.Column('lic_type', sa.String(length=50), nullable=True),
        sa.Column('quantity', sa.Float(precision=7), nullable=True),
        sa.Column('date_created', sa.Date(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_updated', sa.Date(), nullable=True),
        sa.Column('delivery_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['delivery_id'], ['delivery_licence.id'], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )

    op.create_table('licence',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('year', sa.Integer(), nullable=True),
        sa.Column('licence_id', sa.Integer(), nullable=True),
        sa.Column('chemical_name', sa.String(length=100), nullable=True),
        sa.Column('organization_country_name', sa.String(length=4), nullable=True),
        sa.Column('organization_country_name_orig', sa.String(length=100), nullable=True),
        sa.Column('custom_procedure_name', sa.String(length=100), nullable=True),
        sa.Column('international_party_country_name', sa.String(length=100), nullable=True),
        sa.Column('international_party_country_name_orig', sa.String(length=100), nullable=True),
        sa.Column('qty_qdp_percentage', sa.Float(precision=7), nullable=True),
        sa.Column('qty_percentage', sa.Float(precision=7), nullable=True),
        sa.Column('licence_state', sa.String(length=50), nullable=True),
        sa.Column('long_licence_number', sa.String(length=50), nullable=True),
        sa.Column('template_detailed_use_code', sa.String(length=255), nullable=True),
        sa.Column('licence_type', sa.String(length=50), nullable=True),
        sa.Column('mixture_nature_type', sa.String(length=50), nullable=True),
        sa.Column('date_created', sa.Date(), server_default=sa.text('now()'), nullable=True),
        sa.Column('date_updated', sa.Date(), nullable=True),
        sa.Column('substance_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['substance_id'], ['substance.id'], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint('id')
    )


def downgrade():
    op.drop_table('licence')
    op.drop_table('substance')
    op.drop_table('delivery_licence')
    op.drop_table('substance_name_conversion')
    op.drop_table('licence_details_conversion')
    op.drop_table('country_codes_conversion')
