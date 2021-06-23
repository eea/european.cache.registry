revision = "0013"
down_revision = "0012"

from alembic import op


def upgrade():
    op.drop_constraint("email", "user", type_="unique")


def downgrade():
    op.create_unique_constraint(u"email", "user", ["email"])
