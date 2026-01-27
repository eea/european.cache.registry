# coding: utf-8

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db


class Country(SerializableModel, db.Model):
    __tablename__ = "country"

    id = Column(Integer, primary_key=True)
    code = Column(String(10))
    name = Column(String(255))
    type = Column(String(64))


class Address(SerializableModel, db.Model):
    __tablename__ = "address"

    id = Column(Integer, primary_key=True)
    street = Column(String(255))
    number = Column(String(64))
    zipcode = Column(String(64))
    city = Column(String(255))
    country_id = Column(ForeignKey("country.id"))

    country = relationship(Country)

    def __repr__(self):
        return self.zipcode
