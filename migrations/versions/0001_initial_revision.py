revision = "0001"
down_revision = None

from alembic import op
import sqlalchemy as sa


def upgrade():
    op.create_table(
        "businessprofile",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("highleveluses", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "country",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("code", sa.String(length=10), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("type", sa.String(length=64), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "old_company",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("country_code", sa.String(length=10), nullable=True),
        sa.Column("account", sa.String(length=255), nullable=True),
        sa.Column("vat_number", sa.String(length=32), nullable=True),
        sa.Column("eori", sa.String(length=32), nullable=True),
        sa.Column("active", sa.Boolean(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("date_registered", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "user",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("username", sa.String(length=255), nullable=True),
        sa.Column("first_name", sa.String(length=255), nullable=True),
        sa.Column("last_name", sa.String(length=255), nullable=True),
        sa.Column("email", sa.String(length=255), nullable=True),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "address",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("street", sa.String(length=255), nullable=True),
        sa.Column("number", sa.String(length=64), nullable=True),
        sa.Column("zipcode", sa.String(length=16), nullable=True),
        sa.Column("city", sa.String(length=255), nullable=True),
        sa.Column("country_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["country_id"],
            ["country.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "represent",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("vatnumber", sa.String(length=255), nullable=True),
        sa.Column("contact_first_name", sa.String(length=255), nullable=True),
        sa.Column("contact_last_name", sa.String(length=255), nullable=True),
        sa.Column("contact_email", sa.String(length=255), nullable=True),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["address.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "undertaking",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("external_id", sa.Integer(), nullable=True),
        sa.Column("name", sa.String(length=255), nullable=True),
        sa.Column("address_id", sa.Integer(), nullable=True),
        sa.Column("website", sa.String(length=255), nullable=True),
        sa.Column("phone", sa.String(length=32), nullable=True),
        sa.Column("domain", sa.String(length=32), nullable=True),
        sa.Column("date_created", sa.Date(), nullable=True),
        sa.Column("date_updated", sa.Date(), nullable=True),
        sa.Column("status", sa.String(length=64), nullable=True),
        sa.Column("undertaking_type", sa.String(length=32), nullable=True),
        sa.Column("vat", sa.String(length=255), nullable=True),
        sa.Column("types", sa.String(length=255), nullable=True),
        sa.Column("represent_id", sa.Integer(), nullable=True),
        sa.Column("businessprofile_id", sa.Integer(), nullable=True),
        sa.Column("oldcompany_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["address_id"],
            ["address.id"],
        ),
        sa.ForeignKeyConstraint(
            ["businessprofile_id"],
            ["businessprofile.id"],
        ),
        sa.ForeignKeyConstraint(
            ["oldcompany_id"], ["old_company.id"], name="fk_old_company"
        ),
        sa.ForeignKeyConstraint(
            ["represent_id"],
            ["represent.id"],
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_table(
        "old_company_link",
        sa.Column("oldcompany_id", sa.Integer(), nullable=False),
        sa.Column("undertaking_id", sa.Integer(), nullable=False),
        sa.Column("verified", sa.Boolean(), nullable=True),
        sa.Column("date_added", sa.DateTime(), nullable=True),
        sa.Column("date_verified", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(
            ["oldcompany_id"],
            ["old_company.id"],
        ),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.PrimaryKeyConstraint("oldcompany_id", "undertaking_id"),
    )
    op.create_table(
        "undertaking_users",
        sa.Column("user_id", sa.Integer(), nullable=True),
        sa.Column("undertaking_id", sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(
            ["undertaking_id"],
            ["undertaking.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["user.id"],
        ),
    )
    op.create_unique_constraint(u"email", "user", ["email"])


def downgrade():
    op.drop_table("undertaking_users")
    op.drop_table("old_company_link")
    op.drop_table("undertaking")
    op.drop_table("represent")
    op.drop_table("address")
    op.drop_table("user")
    op.drop_table("old_company")
    op.drop_table("country")
    op.drop_table("businessprofile")
