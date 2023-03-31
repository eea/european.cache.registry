from alembic import op
import sqlalchemy as sa

revision = "0029"
down_revision = "0028"


def upgrade():
    op.create_table(
        "stock",
        sa.Column("year", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=255), nullable=True),
        sa.Column("substance_name_form", sa.String(length=255), nullable=False),
        sa.Column("is_virgin", sa.Boolean(), nullable=True),
        sa.Column("code", sa.String(length=50), nullable=False),
        sa.Column("result", sa.Integer(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("year", "substance_name_form", "code", "type"),
    )


def downgrade():
    op.drop_table("stock")
