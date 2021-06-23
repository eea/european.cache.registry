revision = "0012"
down_revision = "0011"

from alembic import op


def upgrade():
    op.create_unique_constraint("uniq_mail_const", "mail_address", ["mail"])


def downgrade():
    op.drop_constraint("uniq_mail_const", "mail_address")
