# coding: utf-8
from datetime import date
from sqlalchemy import (
    Column, Date, DateTime, Float, ForeignKey, Integer, LargeBinary,
    SmallInteger, String, Table, Text, Boolean
)
from sqlalchemy.orm import relationship
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.script import Manager


db = SQLAlchemy()
Base = db.Model
db_manager = Manager()


class SerializableModel(object):
    def get_serialized(self, name):
        value = getattr(self, name)
        if isinstance(value, date):
            value = value.strftime('%d/%m/%Y')
        return value

    def as_dict(self):
        return {c.name: self.get_serialized(c.name) for c in
                self.__table__.columns}


class User(SerializableModel, Base):
    __tablename__ = 'user'

    id = Column(Integer, primary_key=True)
    username = Column(String(255))
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))


class Country(SerializableModel, Base):
    __tablename__ = 'country'

    id = Column(Integer, primary_key=True)
    code = Column(String(10))
    name = Column(String(64))
    type = Column(Integer)


class Address(SerializableModel, Base):
    __tablename__ = 'address'

    id = Column(Integer, primary_key=True)
    street = Column(String(255))
    number = Column(String(10))
    zipcode = Column(String(16))
    city = Column(String(255))
    country_id = Column(ForeignKey('country.id'))

    country = relationship(Country)


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


class BusinessProfile(SerializableModel, Base):
    __tablename__ = 'businessprofile'

    id = Column(Integer, primary_key=True)
    highleveluses = Column(String(255))


undertaking_users = db.Table(
    'undertaking_users',
    db.Column('user_id', db.Integer(),
              db.ForeignKey('user.id')),
    db.Column('undertaking_id', db.Integer(), db.ForeignKey('undertaking.id')),
)


class Undertaking(SerializableModel, Base):
    __tablename__ = 'undertaking'

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
    status = Column(Integer)
    # Undertaking:
    vat = Column(String)
    types = Column(String)
    represent_id = Column(ForeignKey('represent.id'))
    businessprofile_id = Column(ForeignKey('businessprofile.id'))
    # Link
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
        return (
            self.address and self.address.country and self.address.country.code
        )

    @property
    def old_account(self):
        return self.oldcompany and self.oldcompany.account


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


class OldCompanyLink(SerializableModel, Base):
    __tablename__ = 'old_company_link'

    oldcompany_id = Column(ForeignKey('old_company.id'), primary_key=True)
    undertaking_id = Column(ForeignKey('undertaking.id'), primary_key=True)
    verified = Column(Boolean, default=False)
    date_added = Column(DateTime)
    date_verified = Column(DateTime)

    oldcompany = relationship('OldCompany')
    undertaking = relationship('Undertaking', backref=db.backref('links'))


@db_manager.command
def init():
    return db.create_all()

