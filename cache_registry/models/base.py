# coding: utf-8
from datetime import date, datetime
import enum
import json
import os

from flask_sqlalchemy import SQLAlchemy

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
