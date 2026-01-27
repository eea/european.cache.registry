# coding: utf-8

from sqlalchemy import (
    Column,
    ForeignKey,
    Integer,
    String,
)
from sqlalchemy.orm import relationship

from cache_registry.models.base import SerializableModel, db


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
