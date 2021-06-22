revision = '0028'
down_revision = '0027'

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column('substance', 's_organization_country_name',
                    existing_type=sa.String(length=100), new_column_name='s_orig_country_name')


def downgrade():
    op.alter_column('substance', 's_orig_country_name',
                    existing_type=sa.String(length=100), new_column_name='s_organization_country_name')