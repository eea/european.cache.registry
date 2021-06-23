revision = "0032"
down_revision = "0031"

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "process_agent_use",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("type", sa.String(length=100), nullable=True),
        sa.Column("substance", sa.String(length=255), nullable=True),
        sa.Column("member_state", sa.String(length=10), nullable=True),
        sa.Column("pau_use", sa.String(length=255), nullable=True),
        sa.Column("value", sa.Integer(), nullable=True),
        sa.Column("process_name", sa.String(length=255), nullable=True),
        sa.Column("year", sa.Integer(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade():
    op.drop_table("process_agent_use")
