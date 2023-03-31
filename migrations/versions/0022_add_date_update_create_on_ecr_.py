from alembic import op
import sqlalchemy as sa

revision = "0022"
down_revision = "0021"


def upgrade():
    op.add_column(
        "undertaking",
        sa.Column(
            "date_created_in_ecr",
            sa.Date(),
            server_default=sa.text("now()"),
            nullable=True,
        ),
    )
    op.add_column(
        "undertaking", sa.Column("date_updated_in_ecr", sa.Date(), nullable=True)
    )


def downgrade():
    op.drop_column("undertaking", "date_updated_in_ecr")
    op.drop_column("undertaking", "date_created_in_ecr")
