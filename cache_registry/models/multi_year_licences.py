# coding: utf-8
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db


class MultiYearLicence(SerializableModel, db.Model):
    __tablename__ = "multi_year_licence"

    id = Column(Integer, primary_key=True)
    licence_id = Column(Integer)  # licenceId
    long_licence_number = Column(String(50))  # longLicenceNumber
    status = Column(String(50))  # status
    status_date = Column(Date)  # statusDate
    validity_start_date = Column(Date)  # validityStartDate
    validity_end_date = Column(Date)  # validityEndDate
    licence_type = Column(String(10))  # licenceType
    substance_mixture = Column(String(20))  # substanceMixture
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
    update_date = Column(Date)  # updateDate
    undertaking_id = Column(ForeignKey("undertaking.id"), nullable=True, default=None)
    eu_only_representative_id = Column(
        ForeignKey("represent.id"), nullable=True, default=None
    )
    undertaking = relationship(
        "Undertaking", backref=db.backref("multi_year_licences", lazy="dynamic")
    )  # organisation
    eu_only_representative = relationship(
        "EuLegalRepresentativeCompany",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )  # euOnlyRepresentative

    detailed_uses = relationship(
        "DetailedUse",
        secondary="multi_year_licence_detailed_use_link",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )
    cn_codes = relationship(
        "CombinedNomenclature",
        secondary="multi_year_licence_combined_nomenclature_link",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )
    substance_nomenclatures = relationship(
        "SubstanceNomenclature",
        secondary="multi_year_licence_substance_link",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )


class DetailedUse(SerializableModel, db.Model):
    __tablename__ = "detailed_use"

    id = Column(Integer, primary_key=True)
    short_code = Column(String(20))
    description = Column(String(255))
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)


class MultiYearLicenceDetailedUseLink(SerializableModel, db.Model):
    __tablename__ = "multi_year_licence_detailed_use_link"

    multi_year_licence_id = Column(
        ForeignKey("multi_year_licence.id"), primary_key=True
    )
    detailed_use_id = Column(ForeignKey("detailed_use.id"), primary_key=True)
    valid_until = Column(Date)
    multi_year_licence = relationship(
        "MultiYearLicence",
        cascade="all",
        backref=db.backref("detailed_uses_link"),
    )
    detailed_use = relationship(
        "DetailedUse",
        cascade="all",
        backref=db.backref("multi_year_licences_link"),
    )
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)


class SubstanceNomenclature(SerializableModel, db.Model):
    """Substances covered by multi-year licences"""

    __tablename__ = "substance_nomenclature"

    id = Column(Integer, primary_key=True)
    chemical_name = Column(String(100))  # chemicalName
    name = Column(String(255))  # name
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)


class CombinedNomenclature(SerializableModel, db.Model):
    """CN covered by multi-year licences"""

    __tablename__ = "combined_nomenclature"

    id = Column(Integer, primary_key=True)
    code = Column(String(20))  # code
    description = Column(String(255))  # description
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)


multi_year_licence_combined_nomenclature = db.Table(
    "multi_year_licence_combined_nomenclature_link",
    db.Column(
        "multi_year_licence_id", db.Integer(), db.ForeignKey("multi_year_licence.id")
    ),
    db.Column(
        "combined_nomenclature_id",
        db.Integer(),
        db.ForeignKey("combined_nomenclature.id"),
    ),
)

multi_year_licence_substances = db.Table(
    "multi_year_licence_substance_link",
    db.Column(
        "multi_year_licence_id", db.Integer(), db.ForeignKey("multi_year_licence.id")
    ),
    db.Column(
        "substance_nomenclature_id",
        db.Integer(),
        db.ForeignKey("substance_nomenclature.id"),
    ),
)
