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
