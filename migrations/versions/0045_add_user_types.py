"""empty message

Revision ID: 0045
Revises: 0044
Create Date: 2026-01-26 09:59:47.562501

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "0045"
down_revision = "0044"
branch_labels = None
depends_on = None


old_options = (
    "AUDITOR_ORG_FGAS",
    "AUDITOR_ORG_AND_VERIFIER",
    "AUDITOR_ORG_ONLY_VERIFIER",
)
new_options = sorted(old_options + ("ORGANISATION_USER", "EUONLYREPRESENTATIVE_USER"))

old_type = sa.Enum(*old_options, name="usertype")
new_type = sa.Enum(*new_options, name="usertype")
tmp_type = sa.Enum(*new_options, name="_usertype")

tcr = sa.sql.table("user", sa.Column("type", new_type, nullable=False))


def upgrade():
    # Create a tempoary "_usertype" type, convert and drop the "old" usertype
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE public.user ALTER COLUMN type TYPE _usertype"
        " USING type::text::_usertype"
    )
    old_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "new" type usertype
    new_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE public.user ALTER COLUMN type TYPE usertype"
        " USING type::text::usertype"
    )
    tmp_type.drop(op.get_bind(), checkfirst=False)


def downgrade():
    # Convert 'output_limit_exceeded' type into 'timed_out'
    op.execute(
        tcr.update()
        .where(tcr.c.type == "output_limit_exceeded")
        .values(status="timed_out")
    )
    # Create a tempoary "_usertype" type, convert and drop the "new" type
    tmp_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE public.user ALTER COLUMN type TYPE _usertype"
        " USING type::text::_usertype"
    )
    new_type.drop(op.get_bind(), checkfirst=False)
    # Create and convert to the "old" type type
    old_type.create(op.get_bind(), checkfirst=False)
    op.execute(
        "ALTER TABLE public.user ALTER COLUMN type TYPE usertype"
        " USING type::text::usertype"
    )
    tmp_type.drop(op.get_bind(), checkfirst=False)
