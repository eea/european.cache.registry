from alembic import op

revision = "0013"
down_revision = "0012"


def upgrade():
    op.drop_constraint("email", "user", type_="unique")


def downgrade():
    op.create_unique_constraint("email", "user", ["email"])
