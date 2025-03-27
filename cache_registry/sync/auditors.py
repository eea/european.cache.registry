from copy import deepcopy
from flask import current_app

from cache_registry.models import db, Address, Auditor
from cache_registry.sync import parsers
from cache_registry.sync.auth import patch_users
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.utils import (
    get_logger,
    get_response,
    update_contact_persons,
    update_ms_accreditation_issuing_countries,
)


def get_latest_auditors(updated_since=None, page_size=None, uid=""):
    """Get latest auditors from specific API url"""

    url = get_absolute_url("API_URL_FGAS", "/latest/auditor/")
    params = {}

    if uid:
        return [get_response(f"{url}{uid}", params)]

    if updated_since:
        params["updatedSince"] = updated_since.strftime("%d/%m/%Y")

    if page_size:
        params["pageSize"] = page_size
        params["pageNumber"] = 1

    return get_response(url, params)


def add_updates_log(auditor, data):
    existing_auditor_data = f"""
        Auditor UID: {auditor.auditor_uid}
        Auditor Name: {auditor.name}
        Auditor Status: {auditor.status}
        Auditor date_created: {auditor.date_created}
        Auditor date_updated: {auditor.date_updated}
        Auditor date_created_in_ecr: {auditor.date_created_in_ecr}
        Auditor date_updated_in_ecr: {auditor.date_updated_in_ecr}
    """
    received_auditor_data = f"Received data: {data}"
    message = f"""
        Auditor {auditor.auditor_uid} updated: \n \
        Old data: {existing_auditor_data} New data: {received_auditor_data}"
    """
    logger = get_logger("updated")
    logger.info(message)


def patch_auditor(auditor_uid, data):
    patch = current_app.config.get("PATCH_AUDITORS", {})
    if auditor_uid in patch:
        print(f"Patching auditor: {auditor_uid}")
        data.update(patch[auditor_uid])
    return data


def update_auditor(original_data):
    """Create or update auditor from received data"""

    data = deepcopy(original_data)
    data = patch_auditor(data["auditorUID"], data)
    address = parsers.parse_address(data.pop("address"))
    contact_persons = parsers.parse_cp_list(data.pop("contactPersons", []))
    contact_persons, _ = patch_users(
        data["auditorUID"], contact_persons, "PATCH_AUDITOR_USERS", "auditor"
    )
    data["auditor_uid"] = data.pop("auditorUID")
    data["ets_accreditation"] = data.pop("etsAccreditation").get("enabled")
    ms_accreditation = parsers.parse_ms_accreditation(data.pop("msAccreditation"))
    data["ms_accreditation"] = ms_accreditation["ms_accreditation"]

    data["date_created"] = parsers.parse_date(data.pop("dateCreated"))
    data["date_updated"] = parsers.parse_date(data.pop("dateUpdated"))

    auditor = Auditor.query.filter_by(auditor_uid=data["auditor_uid"]).first()
    if not auditor:
        auditor = Auditor(**data)
    else:
        add_updates_log(auditor, original_data)
        parsers.update_obj(auditor, data)

    db.session.add(auditor)
    if not auditor.address:
        addr = Address(**address)
        db.session.add(addr)
        auditor.address = addr
    else:
        parsers.update_obj(auditor.address, address)
    update_contact_persons(auditor, contact_persons)
    update_ms_accreditation_issuing_countries(auditor, ms_accreditation)
