# coding: utf-8
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    Date,
    DateTime,
    Integer,
    String,
)

from cache_registry.models.base import SerializableModel, db


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
