revision = '0019'
down_revision = '0018'
import sqlalchemy as sa

from alembic import op
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship

from cache_registry.models import loaddata

Session = sessionmaker()
Base = declarative_base()


class BusinessProfile(Base):
    __tablename__ = 'businessprofile'

    id = sa.Column(sa.Integer, primary_key=True)
    highleveluses = sa.Column(sa.String(900))


class Undertaking(Base):
    __tablename__ = 'undertaking'

    id = sa.Column(sa.Integer, primary_key=True)
    domain = sa.Column(sa.String(32), nullable=False)
    businessprofile_id = sa.Column(sa.ForeignKey('businessprofile.id'))
    businessprofile = relationship('BusinessProfile')


class UndertakingBusinessProfile(Base):
    __tablename__ = 'undertaking_businessprofile'

    undertaking_id = sa.Column(sa.ForeignKey('undertaking.id'),
                               primary_key=True)
    businessprofile_id = sa.Column(sa.ForeignKey('businessprofile.id'),
                                   primary_key=True)


def upgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    UndertakingBusinessProfile.__table__.create(bind)

    undertaking_businessprofiles = {}
    for undertaking in session.query(Undertaking):
        if not undertaking.businessprofile:
            continue
        profiles = undertaking.businessprofile.highleveluses.split(',')
        undertaking_businessprofiles[undertaking.id] = profiles
    op.drop_column(u'undertaking', 'businessprofile_id')
    session.query(BusinessProfile).delete()

    op.add_column(
            u'businessprofile',
            sa.Column('domain', sa.String(length=32))
    )
    loaddata('cache_registry/fixtures/business_profiles.json', session=session)
    m2m_values = []
    for undertaking_id, highleveluses in undertaking_businessprofiles.items():

        for use in highleveluses:
            if not use:
                continue
            businessprofile_id = session.query(BusinessProfile).filter_by(
                highleveluses=use
            ).first().id
            m2m_values.append(
                {
                    'undertaking_id': undertaking_id,
                    'businessprofile_id': businessprofile_id
                }
            )
    op.bulk_insert(UndertakingBusinessProfile.__table__, m2m_values)


def downgrade():
    bind = op.get_bind()
    session = Session(bind=bind)

    op.add_column(
        u'undertaking',
        sa.Column(
            'businessprofile_id',
            sa.Integer(),
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
                undertaking_id=undertaking.id
            )
        ]
        if not businessprofile_ids:
            continue
        businessprofile_values = [
            businessprofile.highleveluses.strip() for businessprofile in
            session.query(BusinessProfile).filter(
                BusinessProfile.id.in_(businessprofile_ids)
            )
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
    op.drop_table('undertaking_businessprofile')
    session.query(BusinessProfile).delete()
    op.bulk_insert(BusinessProfile.__table__, old_format_businessprofile_values)
