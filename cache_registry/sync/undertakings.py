import requests
import logging
from logging.handlers import RotatingFileHandler
from flask import current_app

from cache_registry.models import (
    Address,
    BusinessProfile,
    EuLegalRepresentativeCompany,
    Type,
    Undertaking,
    UndertakingBusinessProfile,
    UndertakingTypes,
    User,
)
from cache_registry.models import db
from cache_registry.sync import parsers
from instance.settings import FGAS, ODS
from .bdr import update_bdr_col_name, get_absolute_url
from .auth import get_auth, Unauthorized, InvalidResponse, patch_users


def get_logger(module_name):
    """Generate a logger."""
    logger = logging.getLogger(module_name)
    log_file_updated = "ecr_updates_logging.log"
    logger.setLevel(logging.INFO)
    logger.propagate = False
    file_handler_updates = RotatingFileHandler(
        log_file_updated, maxBytes=20971520, backupCount=1
    )  # 20mb
    logger.handlers = [file_handler_updates]
    return logger


def get_latest_undertakings(
    type_url, updated_since=None, page_size=None, id=None, domain=FGAS
):
    """Get latest undertakings from specific API url"""
    auth = get_auth("API_USER", "API_PASSWORD")
    if domain == FGAS:
        url = get_absolute_url("API_URL_FGAS", type_url)
    else:
        url = get_absolute_url("API_URL_ODS", type_url)
    if updated_since:
        updated_since = updated_since.strftime("%d/%m/%Y")
        params = {"updatedSince": updated_since}
    else:
        params = {}

    if id:
        params["organizationId"] = id

    headers = dict(zip(("user", "password"), auth))
    ssl_verify = current_app.config["HTTPS_VERIFY"]

    if page_size:
        params["pageSize"] = page_size
        params["pageNumber"] = 1

    response = requests.get(url, params=params, headers=headers, verify=ssl_verify)

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    if not page_size:
        return response.json()
    try:
        no_of_pages = int(response.headers["numberOfPages"])
    except:
        no_of_pages = 1
    response_json = response.json()

    for page_number in range(2, no_of_pages + 1):
        params["pageNumber"] = page_number
        response = requests.get(url, params=params, headers=headers, verify=ssl_verify)
        if response.status_code != 200:
            raise InvalidResponse()
        response_json += response.json()

    return response_json


def patch_undertaking(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get("PATCH_COMPANIES", {})
    if external_id in patch:
        print("Patching undertaking: {}".format(external_id))
        data.update(patch[external_id])
    return data


def patch_undertaking_old_gb_represent(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get("PATCH_GB_OLD_REPR", {})
    if external_id in patch:
        represent = data.get("euLegalRepresentativeCompany")
        if not represent:
            print("Patching old gb represent on undertaking: {}".format(external_id))
            data.update(patch[external_id])
    return data


def add_updates_log(undertaking, data):

    existing_undertaking_data = """   
        Organisation ID: {}
        Organisation Name: {}
        Organisation Status: {}
        Organisation Domain: {}
        Organisation type: {}
        Organisation Country code: {}
        Organisation Country code orig: {}
        Organisation vat: {}
        Organisation check_passed: {}
        Organisation date_created: {}
        Organisation date_updated: {}
        Organisation date_created_in_ecr: {}
        Organisation date_updated_in_ecr: {}
        Organisation country_history: {}
        Organisation types: {}
        Organisation represent: {}
        Organisation represent_history: {}
        Organisation businessprofiles: {}

    """.format(
        undertaking.external_id,
        undertaking.name,
        undertaking.status,
        undertaking.domain,
        undertaking.undertaking_type,
        undertaking.country_code,
        undertaking.country_code_orig,
        undertaking.vat,
        undertaking.check_passed,
        undertaking.date_created,
        undertaking.date_updated,
        undertaking.date_created_in_ecr,
        undertaking.date_updated_in_ecr,
        [x.code for x in undertaking.country_history],
        [x.type for x in undertaking.types],
        undertaking.represent,
        undertaking.represent_history,
        [x.highleveluses for x in undertaking.businessprofiles],
    )
    received_undertaking_data = """   
        Received data: {}
    """.format(
        data,
    )
    message = f"Undertaking {undertaking.external_id} updated: \n Old data: {existing_undertaking_data} New data: {received_undertaking_data}"
    logger = get_logger("updated")
    logger.info(message)


def update_undertaking(data, check_passed=True):
    """Create or update undertaking from received data"""
    original_data = data.copy()
    represent_changed = False
    data = patch_undertaking(data["id"], data)
    address = parsers.parse_address(data.pop("address"))
    business_profiles = data.pop("businessProfile")
    contact_persons = parsers.parse_cp_list(data.pop("contactPersons"))
    types = data.pop("types")
    if not data["domain"] == ODS:
        represent = parsers.parse_rc(data.pop("euLegalRepresentativeCompany"))
    contact_persons, is_patched = patch_users(data["id"], contact_persons)
    data["external_id"] = data.pop("id")
    data["date_created"] = parsers.parse_date(data.pop("dateCreated"))
    data["date_updated"] = parsers.parse_date(data.pop("dateUpdated"))
    data["undertaking_type"] = data.pop("@type", None)
    data["eori_number"] = data.pop("eori", "")
    if data["domain"] == ODS:
        represent = None
        data["vat"] = data.pop("eoriNumber")

    data["check_passed"] = check_passed

    undertaking = Undertaking.query.filter_by(
        external_id=data["external_id"], domain=data["domain"]
    ).first()
    if not undertaking:
        represent_changed = True
        undertaking = Undertaking(**data)
    else:
        undertaking.types.clear()
        undertaking.businessprofiles.clear()
        add_updates_log(undertaking, original_data)
        u_name = undertaking.name
        parsers.update_obj(undertaking, data)
        if undertaking.name != u_name:
            if update_bdr_col_name(undertaking):
                print(
                    "Updated collection title for: {0}".format(undertaking.external_id)
                )
    if not undertaking.address:
        addr = Address(**address)
        db.session.add(addr)
        undertaking.address = addr
    else:
        if undertaking.address.country.code != address["country"].code:
            if undertaking.address.country not in undertaking.country_history:
                undertaking.country_history.append(undertaking.address.country)
        parsers.update_obj(undertaking.address, address)
    db.session.add(undertaking)
    UndertakingBusinessProfile.query.filter_by(undertaking=undertaking).delete()
    for business_profile in business_profiles["highLevelUses"]:
        business_profile_object = BusinessProfile.query.filter_by(
            highleveluses=business_profile, domain=data["domain"]
        ).first()
        if business_profile_object not in undertaking.businessprofiles:
            undertaking.businessprofiles.append(business_profile_object)

    if not represent:
        old_represent = undertaking.represent
        undertaking.represent = None
        if old_represent:
            undertaking.represent_history.append(old_represent)
            represent_changed = True
    else:
        address = represent.pop("address")
        if not undertaking.represent:
            if undertaking.address.country.type == "AMBIGUOUS_TYPE":
                if undertaking.address.country not in undertaking.country_history:
                    undertaking.country_history.append(undertaking.address.country)
            addr = Address(**address)
            db.session.add(addr)
            r = EuLegalRepresentativeCompany(**represent)
            db.session.add(r)
            undertaking.represent = r
            undertaking.represent.address = addr
            represent_changed = True
        else:
            if represent["vatnumber"] != undertaking.represent.vatnumber:
                undertaking.represent_history.append(undertaking.represent)
                addr = Address(**address)
                db.session.add(addr)
                r = EuLegalRepresentativeCompany(**represent)
                db.session.add(r)
                undertaking.represent = r
                undertaking.represent.address = addr
                represent_changed = True
            else:
                parsers.update_obj(undertaking.represent.address, address)
                parsers.update_obj(undertaking.represent, represent)

    # Update or create types
    UndertakingTypes.query.filter_by(undertaking=undertaking).delete()
    for type in types:
        type_object = Type.query.filter_by(type=type, domain=data["domain"]).first()
        if type_object and type_object not in undertaking.types:
            undertaking.types.append(type_object)

    unique_emails = set([cp.get("email") for cp in contact_persons])
    existing_persons = undertaking.contact_persons
    for contact_person in contact_persons:
        user = None
        username = contact_person["username"]
        # Check if we have a user with that username
        by_username = User.query.filter_by(username=username).first()
        if not by_username:
            email = contact_person["email"]
            # Check if we have a user with that email
            by_email = User.query.filter_by(email=email).first()
            # If we have an email as username, check for duplicate emails
            if "@" in username:
                if len(unique_emails) != len(contact_persons):
                    # If we have duplicate emails, don't match any
                    by_email = None

        user = by_username or by_email

        if user:
            do_update = False
            for key, value in contact_person.items():
                if value != getattr(user, key):
                    do_update = True
            if do_update:
                parsers.update_obj(user, contact_person)
        else:
            user = User(**contact_person)
            db.session.add(user)
        if user not in existing_persons:
            undertaking.contact_persons.append(user)

        current_emails = [p.get("email") for p in contact_persons]
        current_usernames = [p.get("username") for p in contact_persons]
        for person in undertaking.contact_persons:
            if (
                person.email not in current_emails
                or person.username not in current_usernames
            ):
                undertaking.contact_persons.remove(person)

    undertaking.country_code = undertaking.get_country_code()
    undertaking.country_code_orig = undertaking.get_country_code_orig()
    db.session.add(undertaking)
    return (undertaking, represent_changed)


def remove_undertaking(data, domain):
    """Remove undertaking."""

    undertaking = Undertaking.query.filter_by(
        external_id=data.get("id"), domain=domain
    ).first()
    if undertaking:
        msg = "Removing undertaking name: {}" " with id: {}".format(
            undertaking.name, undertaking.id
        )
        current_app.logger.warning(msg)
        undertaking.represent_history = []
        undertaking.types = []
        undertaking.business_profiles = []
        db.session.commit()
        db.session.delete(undertaking)
    else:
        msg = "No company with id: {} found in the db".format(data.get("id"))
        current_app.logger.warning(msg)
