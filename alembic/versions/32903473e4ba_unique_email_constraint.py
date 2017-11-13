revision = '32903473e4ba'
down_revision = '576264dfff3f'

from alembic import op


def upgrade():
    op.create_unique_constraint('uniq_mail_const', 'mail_address', ['mail'])


def downgrade():
    op.drop_constraint('uniq_mail_const', 'mail_address')
