from alembic import op
import sqlalchemy as sa

revision = "0020"
down_revision = "0019"


def upgrade():
    op.create_table(
        "undertaking_represent_history",
        sa.Column("undertaking_id", sa.Integer(), nullable=False),
        sa.Column("represent_id", sa.Integer(), nullable=False),
        sa.ForeignKeyConstraint(
            ["represent_id"],
            ["represent.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("undertaking_id", "represent_id"),
    )
    op.alter_column(
        "matching_log",
        "domain",
        existing_type=sa.VARCHAR(length=32),
        nullable=True,
        existing_server_default=sa.text("'FGAS'::character varying"),
    )
    op.alter_column(
        "organization_log",
        "domain",
        existing_type=sa.VARCHAR(length=32),
        nullable=True,
        existing_server_default=sa.text("'FGAS'::character varying"),
    )
    op.create_foreign_key(None, "undertaking", "old_company", ["oldcompany_id"], ["id"])
    op.create_unique_constraint(None, "user", ["username"])


def downgrade():
    op.drop_constraint(None, "user", type_="unique")
    op.drop_constraint(None, "undertaking", type_="foreignkey")
    op.alter_column(
        "organization_log",
        "domain",
        existing_type=sa.VARCHAR(length=32),
        nullable=False,
        existing_server_default=sa.text("'FGAS'::character varying"),
    )
    op.alter_column(
        "matching_log",
        "domain",
        existing_type=sa.VARCHAR(length=32),
        nullable=False,
        existing_server_default=sa.text("'FGAS'::character varying"),
    )
    op.drop_table("undertaking_represent_history")
