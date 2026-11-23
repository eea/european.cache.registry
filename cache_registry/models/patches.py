# coding: utf-8
from datetime import datetime

from flask import current_app
from sqlalchemy import JSON, Column, DateTime, Integer, String

from cache_registry.models.base import SerializableModel, db

__all__ = ["PATCH_SETTINGS", "PatchSetting", "get_patch"]


# Patch and override settings that can be managed through the API, with the type of value
# each one holds. They used to live only in instance/extra/localsettings.py.
PATCH_SETTINGS = {
    "PATCH_USERS": dict,
    "PATCH_COMPANIES": dict,
    "PATCH_GB_OLD_REPR": dict,
    "PATCH_AUDITORS": dict,
    "PATCH_AUDITOR_USERS": dict,
    "PATCH_LICENCES": list,
    "PATCH_MULTI_YEAR_LICENCES": list,
    "OVERRIDE_LICENCES": list,
    "OVERRIDE_MULTI_YEAR_LICENCES": list,
}


class PatchSetting(SerializableModel, db.Model):
    __tablename__ = "patch_setting"

    id = Column(Integer, primary_key=True)
    name = Column(String(64), unique=True, nullable=False)
    value = Column(JSON, nullable=False)
    date_updated = Column(
        DateTime(timezone=True), default=datetime.now, onupdate=datetime.now
    )


def get_patch(name, default=None):
    """Return a patch setting.

    The value stored in the database wins; if there is none, fall back to the
    value from the settings files (instance/extra/localsettings.py).
    """
    setting = PatchSetting.query.filter_by(name=name).first()
    if setting is not None:
        return setting.value
    return current_app.config.get(name, default)
