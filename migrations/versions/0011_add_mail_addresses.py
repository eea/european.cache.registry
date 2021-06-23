revision = "0011"
down_revision = "0010"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "mail_address",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("mail", sa.String(length=255), nullable=True),
        sa.Column("timestamp", sa.DateTime(), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("mail_address")
