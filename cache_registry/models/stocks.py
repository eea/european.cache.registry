# coding: utf-8
from sqlalchemy import (
    Boolean,
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db


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
