# coding: utf-8
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db
from cache_registry.models import Country


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


class MailAddress(SerializableModel, db.Model):
    __tablename__ = "mail_address"

    id = Column(Integer, primary_key=True)
    mail = Column(String(255), unique=True)
    timestamp = Column(DateTime(timezone=True), default=datetime.now)
    first_name = Column(String(255))
    last_name = Column(String(255))
