# coding: utf-8
from datetime import date

from sqlalchemy import (
    Column,
    Date,
    ForeignKey,
    Integer,
    String,
    Boolean,
)
from sqlalchemy.orm import relationship

from flask_sqlalchemy.query import Query

from instance.settings import FGAS, ODS

from cache_registry.models.base import SerializableModel, db


class DomainQuery(Query):
    def fgases(self):
        return self.filter(Undertaking.domain == FGAS)

    def ods(self):
        return self.filter(Undertaking.domain == ODS)


undertaking_users = db.Table(
    "undertaking_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id"), nullable=False),
    db.Column(
        "undertaking_id", db.Integer(), db.ForeignKey("undertaking.id"), nullable=False
    ),
)


class Undertaking(SerializableModel, db.Model):
    __tablename__ = "undertaking"
    query_class = DomainQuery

    id = Column(Integer, primary_key=True)

    # Organisation
    external_id = Column(Integer)
    registration_id = Column(String(255))
    name = Column(String(255))
    address_id = Column(ForeignKey("address.id"))
    website = Column(String(255))
    phone = Column(String(32))
    domain = Column(String(32), default="FGAS")
    date_created = Column(Date)
    date_updated = Column(Date)
    date_created_in_ecr = Column(Date, default=date.today)
    date_updated_in_ecr = Column(Date, onupdate=date.today)
    status = Column(String(64))
    country_code = Column(String(10), default="")
    country_code_orig = Column(String(10), default="")
    country_history = relationship(
        "Country",
        secondary="undertaking_country_history",
        backref=db.backref("undertakings", lazy="dynamic"),
    )
    # Undertaking:
    undertaking_type = Column(String(32), default="FGASUndertaking")
    vat = Column(String(255))
    eori_number = Column(String(255), default="")
    types = relationship(
        "Type",
        secondary="undertaking_types",
        backref=db.backref("undertaking", lazy="dynamic"),
    )
    represent_id = Column(ForeignKey("represent.id"))

    # Link
    oldcompany_verified = Column(Boolean, default=False)
    oldcompany_account = Column(String(255), nullable=True, default=None)
    oldcompany_extid = Column(Integer, nullable=True, default=None)
    oldcompany_id = Column(ForeignKey("old_company.id"), nullable=True, default=None)
    address = relationship("Address")
    represent = relationship("EuLegalRepresentativeCompany")
    represent_history = relationship(
        "EuLegalRepresentativeCompany",
        secondary="undertaking_represent_history",
        backref=db.backref("undertakings", lazy="dynamic"),
    )
    businessprofiles = relationship(
        "BusinessProfile",
        secondary="undertaking_businessprofile",
        backref=db.backref("undertakings", lazy="dynamic"),
    )
    contact_persons = relationship(
        "User",
        secondary=undertaking_users,
        backref=db.backref("undertakings", lazy="dynamic"),
    )
    oldcompany = relationship("OldCompany", backref=db.backref("undertaking"))
    candidates = relationship(
        "OldCompany",
        secondary="old_company_link",
        lazy="dynamic",
    )

    check_passed = Column(Boolean)

    def get_country_code(self):
        if (
            self.address
            and self.address.country
            and self.address.country.type == "AMBIGUOUS_TYPE"
        ):
            if (
                self.represent
                and self.represent.address
                and self.represent.address.country
            ):
                return self.represent.address.country.code
            else:
                return self.address.country.code
        if (
            self.address
            and self.address.country
            and self.address.country.type == "EU_TYPE"
        ):
            return self.address.country.code
        elif (
            self.represent and self.represent.address and self.represent.address.country
        ):
            return self.represent.address.country.code
        elif (
            len(self.types) >= 1
            and self.types[0].type == "FGAS_MANUFACTURER_OF_EQUIPMENT_HFCS"
        ):
            return "NON_EU"
        else:
            return None

    def get_country_code_orig(self):
        return self.address and self.address.country and self.address.country.code


class BusinessProfile(SerializableModel, db.Model):
    __tablename__ = "businessprofile"

    id = Column(Integer, primary_key=True)
    highleveluses = Column(String(255))
    code = Column(String(255))
    short_code = Column(String(16))
    domain = Column(String(32), default="FGAS")

    def __str__(self):
        return self.code


class UndertakingBusinessProfile(SerializableModel, db.Model):
    __tablename__ = "undertaking_businessprofile"

    undertaking_id = Column(ForeignKey("undertaking.id"), primary_key=True)
    businessprofile_id = Column(ForeignKey("businessprofile.id"), primary_key=True)
    undertaking = relationship(
        "Undertaking",
        backref=db.backref(
            "businessprofiles_link", overlaps="businessprofiles,undertakings"
        ),
        overlaps="businessprofiles,undertakings",
    )
    businessprofile = relationship(
        "BusinessProfile", overlaps="businessprofiles,undertakings"
    )


class Type(SerializableModel, db.Model):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    type = Column(String(255))
    domain = Column(String(32), default="FGAS")


class UndertakingTypes(SerializableModel, db.Model):
    __tablename__ = "undertaking_types"

    undertaking_id = Column(ForeignKey("undertaking.id"), primary_key=True)
    type_id = Column(ForeignKey("type.id"), primary_key=True)
    undertaking = relationship(
        "Undertaking",
        backref=db.backref("types_link", overlaps="types,undertaking"),
        overlaps="types,undertaking",
    )
    type = relationship("Type", overlaps="types,undertaking")


class UndertakingCountryHistory(SerializableModel, db.Model):
    __tablename__ = "undertaking_country_history"

    undertaking_id = Column(ForeignKey("undertaking.id"), primary_key=True)
    country_id = Column(ForeignKey("country.id"), primary_key=True)
    undertaking = relationship(
        "Undertaking",
        cascade="all",
        backref=db.backref(
            "undertaking_country_history_link", overlaps="country_history,undertakings"
        ),
        overlaps="country_history,undertakings",
    )
    country = relationship(
        "Country", cascade="all", overlaps="country_history,undertakings"
    )
