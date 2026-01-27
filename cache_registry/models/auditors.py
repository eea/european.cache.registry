# coding: utf-8
from datetime import date
import enum

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    Enum,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.addresses import Address
from cache_registry.models.users import User
from cache_registry.models.base import SerializableModel, db


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
