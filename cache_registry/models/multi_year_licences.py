# coding: utf-8
from datetime import date

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    ForeignKey,
    Float,
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
        cascade="all",
        secondary="multi_year_licence_combined_nomenclature_link",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )
    substances = relationship(
        "SubstanceNomenclature",
        cascade="all",
        secondary="multi_year_licence_substance_link",
        backref=db.backref("multi_year_licences", lazy="dynamic"),
    )


class MultiYearLicenceAggregated(SerializableModel, db.Model):
    __tablename__ = "multi_year_licence_aggregated"
    """
    Aggregated information about the MultiYearLicence.
    """

    id = Column(Integer, primary_key=True)
    undertaking_id = Column(ForeignKey("undertaking.id"), nullable=True, default=None)
    s_orig_country_name = Column(String(100))  # still not sure how to get this value
    organization_country_name = Column(
        String(4)
    )  # still not sure how to get this value
    year = Column(Integer)
    substance = Column(String(100))
    lic_use_kind = Column(String(100))
    lic_use_desc = Column(String(100))
    lic_type = Column(String(50))
    licence_type = Column(String(10))
    aggregated_reserved_ods_net_mass = Column(Float(precision=7), default=0.0)
    aggregated_consumed_ods_net_mass = Column(Float(precision=7), default=0.0)
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
    created_from_certex = Column(Boolean, default=False)
    has_certex_data = Column(Boolean, default=False)

    undertaking = relationship(
        "Undertaking",
        backref=db.backref("multi_year_licences_aggregated", lazy="dynamic"),
    )  # organisation


class DetailedUse(SerializableModel, db.Model):
    __tablename__ = "detailed_use"

    id = Column(Integer, primary_key=True)
    licence_type = Column(String(10))
    short_code = Column(String(20))
    code = Column(String(255))
    lic_use_desc = Column(String(255))
    lic_type = Column(String(50))
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)
    obsolete = Column(Boolean, default=False)


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
    substances = relationship(
        "SubstanceNomenclature",
        cascade="all",
        secondary="substance_nomenclature_combined_nomenclature_link",
        backref=db.backref("combined_nomenclatures", lazy="dynamic"),
    )


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

substance_nomenclature_combined_nomenclature_link = db.Table(
    "substance_nomenclature_combined_nomenclature_link",
    db.Column(
        "substance_nomenclature_id",
        db.Integer(),
        db.ForeignKey("substance_nomenclature.id"),
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


multi_year_licence_detailed_use_link = db.Table(
    "multi_year_licence_detailed_use_link",
    db.Column(
        "multi_year_licence_id",
        db.Integer(),
        db.ForeignKey("multi_year_licence.id"),
        primary_key=True,
    ),
    db.Column(
        "detailed_use_id",
        db.Integer(),
        db.ForeignKey("detailed_use.id"),
        primary_key=True,
    ),
)
