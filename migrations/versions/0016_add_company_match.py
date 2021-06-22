revision = '0016'
down_revision = '0015'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table('old_company',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('external_id', sa.Integer(), nullable=True),
        sa.Column('name', sa.String(length=255), nullable=True),
        sa.Column('country_code', sa.String(length=10), nullable=True),
        sa.Column('account', sa.String(length=255), nullable=True),
        sa.Column('vat_number', sa.String(length=32), nullable=True),
        sa.Column('eori', sa.String(length=32), nullable=True),
        sa.Column('active', sa.Boolean(), nullable=True),
        sa.Column('website', sa.String(length=255), nullable=True),
        sa.Column('date_registered', sa.DateTime(), nullable=True),
        sa.Column('valid', sa.Boolean(), nullable=True),
        sa.Column('obligation', sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_table('old_company_link',
        sa.Column('oldcompany_id', sa.Integer(), nullable=False),
        sa.Column('undertaking_id', sa.Integer(), nullable=False),
        sa.Column('verified', sa.Boolean(), nullable=True),
        sa.Column('date_added', sa.DateTime(), nullable=True),
        sa.Column('date_verified', sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(['oldcompany_id'], ['old_company.id'], ),
        sa.ForeignKeyConstraint(['undertaking_id'], ['undertaking.id'], ),
        sa.PrimaryKeyConstraint('oldcompany_id', 'undertaking_id'),
    )

    op.add_column(u'matching_log', sa.Column('oldcompany_id', sa.Integer(),
                                             nullable=True))
    op.add_column(u'undertaking', sa.Column('oldcompany_id', sa.Integer(),
                                            nullable=True))


def downgrade():
    op.drop_column(u'undertaking', 'oldcompany_id')
    op.drop_column(u'matching_log', 'oldcompany_id')
    op.drop_table('old_company_link')
    op.drop_table('old_company')
