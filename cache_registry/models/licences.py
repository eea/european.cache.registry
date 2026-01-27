# coding: utf-8
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    Float,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship


from cache_registry.models.base import SerializableModel, db


class Licence(SerializableModel, db.Model):
    __tablename__ = "licence"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    licence_id = Column(Integer)
    chemical_name = Column(String(100))
    organization_country_name = Column(String(4))
    organization_country_name_orig = Column(String(100))
    custom_procedure_name = Column(String(100))
    international_party_country_name = Column(String(100))
    international_party_country_name_orig = Column(String(100))
    total_odp_mass = Column(Float(7))
    net_mass = Column(Float(7))
    licence_state = Column(String(50))
    long_licence_number = Column(String(50))
    template_detailed_use_code = Column(String(255))
    licence_type = Column(String(50))
    mixture_nature_type = Column(String(50))
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
    updated_since = Column(String(30))
    substance_id = Column(ForeignKey("substance.id"), nullable=True, default=None)
    substance = relationship(
        "Substance", cascade="all", backref=db.backref("licences", lazy="dynamic")
    )


class Substance(SerializableModel, db.Model):
    __tablename__ = "substance"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    substance = Column(String(100))
    lic_use_kind = Column(String(100))
    lic_use_desc = Column(String(100))
    lic_type = Column(String(50))
    s_orig_country_name = Column(String(100))
    quantity = Column(Float(precision=7))
    organization_country_name = Column(String(4))

    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)

    delivery_id = Column(ForeignKey("delivery_licence.id"), nullable=True, default=None)
    deliverylicence = relationship(
        "DeliveryLicence",
        cascade="all",
        backref=db.backref("substances", lazy="dynamic"),
    )


class DeliveryLicence(SerializableModel, db.Model):
    __tablename__ = "delivery_licence"

    id = Column(Integer, primary_key=True)
    year = Column(Integer)
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
    updated_since = Column(Date)
    undertaking_id = Column(ForeignKey("undertaking.id"), nullable=True, default=None)
    undertaking = relationship(
        "Undertaking", backref=db.backref("deliveries", lazy="dynamic")
    )


class SubstanceNameConversion(SerializableModel, db.Model):
    __tablename__ = "substance_name_conversion"

    id = Column(Integer, primary_key=True)
    ec_substance_name = Column(String(100))
    corrected_name = Column(String(100))


class CountryCodesConversion(SerializableModel, db.Model):
    __tablename__ = "country_codes_conversion"

    id = Column(Integer, primary_key=True)
    country_name_short_en = Column(String(100))
    country_code_alpha2 = Column(String(5))


class LicenceDetailsConversion(SerializableModel, db.Model):
    __tablename__ = "licence_details_conversion"

    id = Column(Integer, primary_key=True)
    template_detailed_use_code = Column(String(250))
    lic_use_kind = Column(String(100))
    lic_use_desc = Column(String(100))
    lic_type = Column(String(100))
