# coding: utf-8
from datetime import date, datetime
import enum
import json
import os

from sqlalchemy import (
    Column,
    Date,
    DateTime,
    Enum,
    ForeignKey,
    Integer,
    String,
    Boolean,
    Float,
)
from sqlalchemy.orm import relationship

from flask_sqlalchemy.query import Query
from flask_sqlalchemy import SQLAlchemy

from instance.settings import FGAS, ODS

db = SQLAlchemy()


class SerializableModel(object):
    def get_serialized(self, name):
        value = getattr(self, name)
        if isinstance(value, datetime):
            value = value.strftime("%d/%m/%Y %H:%M")
        elif isinstance(value, date):
            value = value.strftime("%d/%m/%Y")
        elif isinstance(value, enum.Enum):
            value = value.value

        return value

    def as_dict(self):
        data = {c.name: self.get_serialized(c.name) for c in self.__table__.columns}
        if "external_id" in data:
            data["company_id"] = data.pop("external_id")
        return data


class User(SerializableModel, db.Model):
    __tablename__ = "user"

    class UserType(enum.Enum):
        AUDITOR_ORG_FGAS = "AUDITOR_ORG_FGAS"
        AUDITOR_ORG_AND_VERIFIER = "AUDITOR_ORG_AND_VERIFIER"
        AUDITOR_ORG_ONLY_VERIFIER = "AUDITOR_ORG_ONLY_VERIFIER"

    id = Column(Integer, primary_key=True)
    ecas_id = Column(String(255))
    username = Column(String(255), unique=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    email = Column(String(255))
    type = Column(Enum(UserType))

    @property
    def verified_undertakings(self):
        return self.undertakings.filter_by(oldcompany_verified=True)

    @property
    def active_auditor_undertakings(self):
        return self.auditor_undertakings.filter_by(end_date=None)


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

    def __unicode__(self):
        return self.zipcode


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


class BusinessProfile(SerializableModel, db.Model):
    __tablename__ = "businessprofile"

    id = Column(Integer, primary_key=True)
    highleveluses = Column(String(255))
    domain = Column(String(32), default="FGAS")

    def __unicode__(self):
        return self.highleveluses


class Type(SerializableModel, db.Model):
    __tablename__ = "type"

    id = Column(Integer, primary_key=True)
    type = Column(String(255))
    domain = Column(String(32), default="FGAS")


auditor_users = db.Table(
    "auditor_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id")),
    db.Column("auditor_id", db.Integer(), db.ForeignKey("auditor.id")),
)


class Auditor(SerializableModel, db.Model):
    __tablename__ = "auditor"

    class Status(enum.Enum):
        DRAFT = "DRAFT"
        SELF_REVISION = "SELF_REVISION"
        SENT_TO_REVISION = "SENT_TO_REVISION"
        REQUESTED = "REQUESTED"
        VALID = "VALID"
        CANCELLED = "CANCELLED"

    id = Column(Integer, primary_key=True)
    auditor_uid = Column(String(20), nullable=False)
    name = Column(String(255), nullable=False)
    address_id = Column(ForeignKey("address.id"), nullable=False)
    website = Column(String(255))
    phone = Column(String(32), nullable=False)
    date_created = Column(Date, nullable=False)
    date_updated = Column(Date, nullable=False)
    date_created_in_ecr = Column(Date, default=date.today, nullable=False)
    date_updated_in_ecr = Column(Date, onupdate=date.today)
    status = Column(Enum(Status), nullable=False)
    ets_accreditation = Column(Boolean, nullable=False)
    ms_accreditation = Column(Boolean, nullable=False)

    # Link
    address = relationship(Address)
    contact_persons = relationship(
        User,
        secondary=auditor_users,
        backref=db.backref("auditors", lazy="dynamic"),
        cascade="all, delete",
    )
    ms_accreditation_issuing_countries = relationship(
        "Country",
        secondary="auditor_ms_accreditation_issuing_countries",
        backref=db.backref("auditors", lazy="dynamic"),
        cascade="all, delete",
    )


auditor_ms_accreditation_issuing_countries = db.Table(
    "auditor_ms_accreditation_issuing_countries",
    db.Column("country_id", db.Integer(), db.ForeignKey("country.id"), nullable=False),
    db.Column("auditor_id", db.Integer(), db.ForeignKey("auditor.id"), nullable=False),
)

undertaking_users = db.Table(
    "undertaking_users",
    db.Column("user_id", db.Integer(), db.ForeignKey("user.id"), nullable=False),
    db.Column(
        "undertaking_id", db.Integer(), db.ForeignKey("undertaking.id"), nullable=False
    ),
)


class DomainQuery(Query):
    def fgases(self):
        return self.filter(Undertaking.domain == FGAS)

    def ods(self):
        return self.filter(Undertaking.domain == ODS)


class Undertaking(SerializableModel, db.Model):
    __tablename__ = "undertaking"
    query_class = DomainQuery

    id = Column(Integer, primary_key=True)

    # Organisation
    external_id = Column(Integer)
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
    address = relationship(Address)
    represent = relationship(EuLegalRepresentativeCompany)
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
        User,
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


class Stock(SerializableModel, db.Model):
    year = Column(Integer, primary_key=True)
    type = Column(String(255), primary_key=True)
    substance_name_form = Column(String(255), primary_key=True)
    is_virgin = Column(Boolean)
    code = Column(String(50), primary_key=True)
    # result provided in kilograms
    result = Column(Integer)
    undertaking_id = Column(ForeignKey("undertaking.id"))
    undertaking = relationship(
        "Undertaking", backref=db.backref("stocks", lazy="dynamic")
    )


class ProcessAgentUse(SerializableModel, db.Model):
    id = Column(Integer, primary_key=True)
    type = Column(String(100))
    substance = Column(String(255))
    member_state = Column(String(10))
    pau_use = Column(String(255))
    value = Column(Integer)
    # process name DG Clima
    process_name = Column(String(255))
    year = Column(Integer)
    undertaking_id = Column(ForeignKey("undertaking.id"))
    undertaking = relationship(
        "Undertaking", backref=db.backref("processagentuses", lazy="dynamic")
    )


class OldCompany(SerializableModel, db.Model):
    __tablename__ = "old_company"

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
    valid = Column(Boolean, default=True)
    obligation = Column(String(32))

    @property
    def country(self):
        country_obj = Country.query.filter_by(code=self.country_code.upper()).first()
        return country_obj and country_obj.name


class OldCompanyLink(SerializableModel, db.Model):
    __tablename__ = "old_company_link"

    oldcompany_id = Column(ForeignKey("old_company.id"), primary_key=True)
    undertaking_id = Column(ForeignKey("undertaking.id"), primary_key=True)
    verified = Column(Boolean, default=False)
    date_added = Column(DateTime)
    date_verified = Column(DateTime)

    oldcompany = relationship("OldCompany", overlaps="candidates")
    undertaking = relationship(
        "Undertaking",
        backref=db.backref("links", overlaps="candidates"),
        overlaps="candidates",
    )


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


class AuditorUndertaking(SerializableModel, db.Model):
    __tablename__ = "auditor_undertaking"
    id = Column(Integer, primary_key=True)
    auditor_id = Column(ForeignKey("auditor.id"))
    undertaking_id = Column(ForeignKey("undertaking.id"))
    user_id = Column(ForeignKey("user.id"))
    start_date = Column(Date, nullable=False)
    end_date = Column(Date)
    reporting_envelope_url = Column(String(128))
    verification_envelope_url = Column(String(128))

    auditor = relationship(
        "Auditor",
        backref=db.backref("auditor_undertakings", lazy="dynamic"),
        overlaps="undertakings",
    )
    undertaking = relationship(
        "Undertaking",
        backref=db.backref("auditor_undertakings", lazy="dynamic"),
        overlaps="undertakings",
    )
    user = relationship(
        "User",
        backref=db.backref("auditor_undertakings", lazy="dynamic"),
        overlaps="undertakings",
    )


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


class OrganizationLog(SerializableModel, db.Model):
    __tablename__ = "organization_log"

    id = Column(Integer, primary_key=True)
    domain = Column(String(32), default="FGAS")
    execution_time = Column(DateTime(timezone=True), default=datetime.now)
    using_last_update = Column(Date)
    organizations = Column(Integer)


class MatchingLog(SerializableModel, db.Model):
    __tablename__ = "matching_log"

    id = Column(Integer, primary_key=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    user = Column(String(255))
    domain = Column(String(32), default="FGAS")
    company_id = Column(Integer)
    oldcompany_id = Column(Integer, nullable=True)
    oldcompany_account = Column(String(255), nullable=True)
    verified = Column(Boolean)


class MailAddress(SerializableModel, db.Model):
    __tablename__ = "mail_address"

    id = Column(Integer, primary_key=True)
    mail = Column(String(255), unique=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    first_name = Column(String(255))
    last_name = Column(String(255))


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


class LicenceDetailsConverstion(SerializableModel, db.Model):
    __tablename__ = "licence_details_conversion"

    id = Column(Integer, primary_key=True)
    template_detailed_use_code = Column(String(250))
    lic_use_kind = Column(String(100))
    lic_use_desc = Column(String(100))
    lic_type = Column(String(100))


def loaddata(fixture, session=None):
    if not session:
        session = db.session
    if not os.path.isfile(fixture):
        print("Please provide a fixture file name")
    else:
        objects = get_fixture_objects(fixture)
    session.commit()
    for object in objects:
        database_object = (
            eval(object["model"]).query.filter_by(id=object["fields"]["id"]).first()
        )
        if not database_object:
            session.add(eval(object["model"])(**object["fields"]))
            session.commit()


def get_fixture_objects(file):
    with open(file) as f:
        return json.loads(f.read())
