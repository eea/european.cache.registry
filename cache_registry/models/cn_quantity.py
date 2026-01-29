# coding: utf-8
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Float,
    Integer,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db


class CNQuantity(SerializableModel, db.Model):
    """
    Information about the quantities for the Multi Year Licences taken from the CERTEX system.
    """

    __tablename__ = "cn_quantity"

    id = Column(Integer, primary_key=True)
    multi_year_licence_id = Column(ForeignKey("multi_year_licence.id"))
    undertaking_id = Column(ForeignKey("undertaking.id"))
    combined_nomenclature_id = Column(ForeignKey("combined_nomenclature.id"))
    year = Column(Integer)  # year
    aggregated_reserved_ods_net_mass = Column(
        Float(precision=7, asdecimal=True), default=0.0
    )
    aggregated_consumed_ods_net_mass = Column(
        Float(precision=7, asdecimal=True), default=0.0
    )
    date_created = Column(Date, default=date.today)
    date_updated = Column(Date, onupdate=date.today)

    undertaking = relationship(
        "Undertaking",
        backref=db.backref("cn_quantities", lazy="dynamic"),
    )
    multi_year_licence = relationship(
        "MultiYearLicence",
        backref=db.backref("cn_quantities"),
    )
    combined_nomenclature = relationship(
        "CombinedNomenclature", backref="cn_quantities"
    )
