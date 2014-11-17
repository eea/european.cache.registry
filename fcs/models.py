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

    address = relationship(Address)
    represent = relationship(EuLegalRepresentativeCompany)
    businessprofile = relationship(BusinessProfile)
    contact_persons = relationship(
        User,
        secondary=undertaking_users,
        backref=db.backref('undertakings', lazy='dynamic'),
        lazy='dynamic',
    )


@db_manager.command
def init():
    return db.create_all()

