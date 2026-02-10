# coding: utf-8

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models import Address
from cache_registry.models.base import SerializableModel, db


class EuLegalRepresentativeCompany(SerializableModel, db.Model):
    __tablename__ = "represent"

    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    address_id = Column(ForeignKey("address.id"))
    vatnumber = Column(String(255))
    contact_first_name = Column(String(255))
    contact_last_name = Column(String(255))
    contact_email = Column(String(255))

    address = relationship(Address)

    def __unicode__(self):
        return self.name


class UndertakingRepresentHistory(SerializableModel, db.Model):
    __tablename__ = "undertaking_represent_history"

    undertaking_id = Column(ForeignKey("undertaking.id"), primary_key=True)
    represent_id = Column(ForeignKey("represent.id"), primary_key=True)
    undertaking = relationship(
        "Undertaking",
        cascade="all",
        backref=db.backref(
            "represent_history_link", overlaps="represent_history,undertakings"
        ),
        overlaps="represent_history,undertakings",
    )
    represent = relationship(
        "EuLegalRepresentativeCompany",
        cascade="all",
        overlaps="represent_history,undertakings",
    )
