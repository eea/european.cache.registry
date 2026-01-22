# coding: utf-8
import enum

from sqlalchemy import (
    Column,
    Enum,
    Integer,
    String,
)
from cache_registry.models.base import SerializableModel, db


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
