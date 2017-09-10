revision = '48d3fd1462da'
down_revision = '3b6b91477843'

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import mysql
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

# Much of the code here is inspired by this:
#  - https://stackoverflow.com/questions/24612395/


Session = sessionmaker()

Base = declarative_base()


# Create minimal versions of the classes to avoid clashes with other versions
# of the table
class BusinessProfile(Base):
    __tablename__ = 'businessprofile'

    id = sa.Column(sa.Integer, primary_key=True)
    highleveluses = sa.Column(sa.String(255))


class Undertaking(Base):
    __tablename__ = 'undertaking'

    id = sa.Column(sa.Integer, primary_key=True)
    domain = sa.Column(sa.String(32), nullable=False)
    businessprofile_id = sa.Column(sa.ForeignKey('businessprofile.id'))
    businessprofile = relationship('BusinessProfile')


class UndertakingBusinessProfile(Base):
    __tablename__ = 'undertaking_businessprofile'
    __table_args__ = ({'mysql_engine': 'MyISAM'},)

    undertaking_id = sa.Column(sa.ForeignKey('undertaking.id'), primary_key=True)
    businessprofile_id = sa.Column(sa.ForeignKey('businessprofile.id'), primary_key=True)


def upgrade():

    bind = op.get_bind()
    session = Session(bind=bind)

    # Start schema migration

    ## Create many-to-many table based on UndertakingBusinessProfile class
    UndertakingBusinessProfile.__table__.create(bind)

    m2m_values = []
    # dict to be filled with business profiles. The items of the dict should be
    # of the following format: {(domain, highleveluses): id}
    businessprofiles = {}
    businessprofile_id = 1

    # Perform data migration in order to preserve the data in columns to be
    # removed/changed
    for undertaking in session.query(Undertaking):
        if not undertaking.businessprofile:
            # If the current undertaking has no businessprofile associated to
            # it, no data will be lost so we don't need to worry about
            # converting it.
            continue

        for profile_str in undertaking.businessprofile.highleveluses.split(','):

            profile_str = profile_str.strip()

            if not profile_str:
                # If the highleveluses of the associated businessprofile was an
                # empty string, once again no data will be lost.
                continue

            # A unique business profile is defined by a domain and a
            # highleveluses value
            businessprofile = (undertaking.domain, profile_str)
            if businessprofile not in businessprofiles:
                businessprofiles[businessprofile] = (
                    businessprofile_id)
                businessprofile_id += 1
            m2m_values.append(
                {
                    'undertaking_id': undertaking.id,
                    'businessprofile_id': businessprofiles[businessprofile]
                }
            )

    # Delete all content from businessprofile table
    session.query(BusinessProfile).delete()
    # Add domain column
    op.add_column(
        u'businessprofile',
        sa.Column('domain', sa.String(length=32))
    )
    # Add unique constrain
    op.create_unique_constraint(
        None, 'businessprofile', ['domain', 'highleveluses'])
    # Update class so it can be used with the new table columns
    BusinessProfile.domain = sa.Column(sa.String(32))

    # Create list with values to be bulk inserted into the businessprofile
    # table with the new format
    businessprofile_values = [
        {
            'id': bp_id,
            'domain': domain,
            'highleveluses': highleveluses
        }
        for (domain, highleveluses), bp_id in businessprofiles.items()
    ]
    # Insert values according to new format
    op.bulk_insert(BusinessProfile.__table__, businessprofile_values)
    # Insert relationships
    op.bulk_insert(UndertakingBusinessProfile.__table__, m2m_values)

    # Once the data is migrated, finish up the schema migration
    op.drop_column(u'undertaking', 'businessprofile_id')


def downgrade():

    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column(
        u'undertaking',
        sa.Column(
            'businessprofile_id',
            mysql.INTEGER(display_width=11),
            autoincrement=False,
            nullable=True
        )
    )
    old_format_businessprofile_values = []
    old_format_businessprofile_id = 1
    for undertaking in session.query(Undertaking):
        businessprofile_ids = [
            link.businessprofile_id for link in
            session.query(UndertakingBusinessProfile).filter_by(
                undertaking_id=undertaking.id)
        ]
        if not businessprofile_ids:
            continue
        businessprofile_values = [
            businessprofile.highleveluses.strip() for businessprofile in
            session.query(BusinessProfile).filter(
                BusinessProfile.id.in_(businessprofile_ids))
            if businessprofile.highleveluses.strip()
        ]
        if not businessprofile_values:
            continue
        old_format_businessprofile_values.append(
            {
                'id': old_format_businessprofile_id,
                'highleveluses': ','.join(businessprofile_values)
            }
        )
        undertaking.businessprofile_id = old_format_businessprofile_id
        old_format_businessprofile_id += 1

    op.drop_column(u'businessprofile', 'domain')
    session.query(BusinessProfile).delete()
    op.bulk_insert(BusinessProfile.__table__, old_format_businessprofile_values)

    op.drop_table('undertaking_businessprofile')
