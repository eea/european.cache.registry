# coding: utf-8
import argparse
from datetime import date, datetime
from sqlalchemy import (
    Column, Date, DateTime, ForeignKey, Integer, String, Boolean
)
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager


db = SQLAlchemy()
Base = db.Model
db_manager = Manager()


class SerializableModel(object):
    EXTRA_FIELDS = []

    def get_serialized(self, name):
        value = getattr(self, name)
        if isinstance(value, datetime):
            value = value.strftime('%d/%m/%Y %H:%M')
        elif isinstance(value, date):
            value = value.strftime('%d/%m/%Y')

        return value

    def as_dict(self):
        data = {c.name: self.get_serialized(c.name) for c in
                self.__table__.columns}
        if 'external_id' in data:
            data['company_id'] = data.pop('external_id')
        data.update(
            {field: self.get_serialized(field) for field in self.EXTRA_FIELDS})
        return data


class User(SerializableModel, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))

    @property
    def verified_undertakings(self):
        return self.undertakings.filter_by(oldcompany_verified=True)


class Country(SerializableModel, Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    code = Column(String(10))
    name = Column(String(255))
    type = Column(String(64))


class Address(SerializableModel, Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    street = Column(String(255))
    number = Column(String(64))
    zipcode = Column(String(16))
    city = Column(String(255))
    country_id = Column(ForeignKey('country.id'))

    country = relationship(Country)

    def __unicode__(self):
        return self.zipcode


class EuLegalRepresentativeCompany(SerializableModel, Base):
    __tablename__ = 'represent'

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address_id = Column(ForeignKey('address.id'))
    vatnumber = Column(String(255))
    contact_first_name = Column(String(255))
    contact_last_name = Column(String(255))
    contact_email = Column(String(255))

    address = relationship(Address)

    def __unicode__(self):
        return self.name


class BusinessProfile(SerializableModel, Base):
    __tablename__ = 'businessprofile'

    id = Column(Integer, primary_key=True)
    highleveluses = Column(String(255))

    def __unicode__(self):
        return self.highleveluses


undertaking_users = db.Table(
    'undertaking_users',
    db.Column('user_id', db.Integer(),
              db.ForeignKey('user.id')),
    db.Column('undertaking_id', db.Integer(), db.ForeignKey('undertaking.id')),
)


class Undertaking(SerializableModel, Base):
    __tablename__ = 'undertaking'
    EXTRA_FIELDS = ('country_code',)

    id = Column(Integer, primary_key=True)

    # Organisation
    external_id = Column(Integer)
    name = Column(String(255))
    address_id = Column(ForeignKey('address.id'))
    website = Column(String(255))
    phone = Column(String(32))
    domain = Column(String(32), default="FGAS")
    date_created = Column(Date)
    date_updated = Column(Date)
    status = Column(String(64))
    # Undertaking:
    undertaking_type = Column(String(32), default='FGASUndertaking')
    vat = Column(String(255))
    types = Column(String(255))
    represent_id = Column(ForeignKey('represent.id'))
    businessprofile_id = Column(ForeignKey('businessprofile.id'))
    # Link
    oldcompany_verified = Column(Boolean, default=False)
    oldcompany_account = Column(String(255), nullable=True, default=None)
    oldcompany_extid = Column(Integer, nullable=True, default=None)
    oldcompany_id = Column(ForeignKey('old_company.id'), nullable=True,
                           default=None)

    address = relationship(Address)
    represent = relationship(EuLegalRepresentativeCompany)
    businessprofile = relationship(BusinessProfile)
    contact_persons = relationship(
        User,
        secondary=undertaking_users,
        backref=db.backref('undertakings', lazy='dynamic'),
        lazy='dynamic',
    )
    oldcompany = relationship('OldCompany', backref=db.backref('undertaking'))
    candidates = relationship(
        'OldCompany',
        secondary='old_company_link',
        lazy='dynamic',
    )

    @property
    def country_code(self):
        if (self.address and self.address.country and
                self.address.country.type == 'EU_TYPE'):
            return self.address.country.code
        elif (self.represent and self.represent.address and
                self.represent.address.country):
            return self.represent.address.country.code
        else:
            return None


class OldCompany(SerializableModel, Base):
    __tablename__ = 'old_company'

    id = Column(Integer, primary_key=True)
    external_id = Column(Integer)
    name = Column(String(255))
    country_code = Column(String(10))
    account = Column(String(255))
    vat_number = Column(String(32))
    eori = Column(String(32))
    active = Column(Boolean)
    website = Column(String(255))
    date_registered = Column(DateTime)
    valid = Column(Boolean, default=True)

    @property
    def country(self):
        country_obj = Country.query.filter_by(
            code=self.country_code.upper()).first()
        return country_obj and country_obj.name


class OldCompanyLink(SerializableModel, Base):
    __tablename__ = 'old_company_link'

    oldcompany_id = Column(ForeignKey('old_company.id'), primary_key=True)
    undertaking_id = Column(ForeignKey('undertaking.id'), primary_key=True)
    verified = Column(Boolean, default=False)
    date_added = Column(DateTime)
    date_verified = Column(DateTime)

    oldcompany = relationship('OldCompany')
    undertaking = relationship('Undertaking', backref=db.backref('links'))


class OrganizationLog(SerializableModel, db.Model):
    __tablename__ = 'organization_log'

    id = Column(Integer, primary_key=True)
    execution_time = Column(DateTime, default=datetime.utcnow)
    using_last_update = Column(Date)
    organizations = Column(Integer)
    for_username = Column(Boolean)


class MatchingLog(SerializableModel, db.Model):
    __tablename__ = 'matching_log'

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime, default=datetime.utcnow)
    user = Column(String(255))
    company_id = Column(Integer)
    oldcompany_id = Column(Integer, nullable=True)
    oldcompany_account = Column(String(255), nullable=True)
    verified = Column(Boolean)


@db_manager.command
def init():
    db.create_all()
    alembic(['stamp', 'head'])


@db_manager.option('alembic_args', nargs=argparse.REMAINDER)
def alembic(alembic_args):
    from alembic.config import CommandLine

    CommandLine().main(argv=alembic_args)


@db_manager.command
def revision(message=None):
    if message is None:
        message = raw_input('revision name: ')
    return alembic(['revision', '--autogenerate', '-m', message])


@db_manager.command
def upgrade(revision='head'):
    return alembic(['upgrade', revision])


@db_manager.command
def downgrade(revision):
    return alembic(['downgrade', revision])
