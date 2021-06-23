revision = "0033"
down_revision = "0032"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=sa.Float(precision=7),
        type_=sa.Integer(),
    )


def downgrade():
    op.alter_column(
        "substance",
        "quantity",
        nullable=True,
        existing_type=sa.Integer(),
        type_=sa.Float(precision=7),
    )
