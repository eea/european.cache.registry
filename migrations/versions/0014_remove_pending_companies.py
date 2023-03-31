from alembic import op
import sqlalchemy as sa

revision = "0014"
down_revision = "0013"


def upgrade():
    op.drop_table("old_company_link")
    op.drop_constraint("fk_old_company", "undertaking", "foreignkey")
    op.drop_column("undertaking", "oldcompany_id")
    op.drop_table("old_company")
    op.drop_column("matching_log", "oldcompany_id")


def downgrade():
    op.create_table(
        "old_company_link",
        sa.Column("oldcompany_id", sa.Integer(), nullable=False, autoincrement=False),
        sa.Column("undertaking_id", sa.Integer(), nullable=False, autoincrement=False),
        sa.Column("verified", sa.Boolean(), nullable=True, autoincrement=False),
        sa.Column("date_added", sa.DateTime(), nullable=True),
        sa.Column("date_verified", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("oldcompany_id", "undertaking_id"),
    )
    op.create_table(
        "old_company",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True, autoincrement=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("country_code", sa.String(length=10), nullable=True),
        sa.Column("account", sa.String(length=255), nullable=True),
        sa.Column("vat_number", sa.String(length=32), nullable=True),
        sa.Column("eori", sa.String(length=32), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("date_registered", sa.DateTime(), nullable=True),
        sa.Column("valid", sa.Boolean(), autoincrement=False, nullable=True),
        sa.Column("obligation", sa.String(length=32), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.add_column(
        "undertaking",
        sa.Column(
            "oldcompany_id",
            sa.Integer(),
            autoincrement=False,
            nullable=True,
            default=None,
        ),
    )
    op.add_column(
        "matching_log",
        sa.Column(
            "oldcompany_id",
            sa.Integer(),
            autoincrement=False,
            nullable=True,
            default=None,
        ),
    )
