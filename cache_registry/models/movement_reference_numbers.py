# coding: utf-8
from datetime import date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


from cache_registry.models.base import SerializableModel, db


class MovementReferenceNumber(SerializableModel, db.Model):  # MRN
    __tablename__ = "movement_reference_number"
    id = Column(Integer, primary_key=True)
    undertaking_id = Column(ForeignKey("undertaking.id"), nullable=False)
    multi_year_licence_id = Column(ForeignKey("licence.id"))
    ghost_licence_number = Column(Boolean, nullable=False)
    mrn = Column(String(32), nullable=False)
    quantities = relationship(
        "CertExQuantity",
        backref="movement_reference_number",
        cascade="all, delete-orphan",
        lazy="dynamic",
    )
    undertaking = relationship("Undertaking")

    undertaking = relationship(
        "Undertaking", backref=db.backref("movement_reference_numbers", lazy="dynamic")
    )  # organisation
    multi_year_licence = relationship(
        "MultiYearLicence",
        backref=db.backref("movement_reference_numbers", lazy="dynamic"),
    )  # multiYearLicence

    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)


class CNQuantity(SerializableModel, db.Model):
    __tablename__ = "cn_quantity"

    id = Column(Integer, primary_key=True)
    combined_nomenclature_id = Column(
        ForeignKey("combined_nomenclature.id"), nullable=False
    )
    reserved_ods_net_mass = Column(Float(7, asdecimal=True))
    consumed_ods_net_mass = Column(Float(7, asdecimal=True))

    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
