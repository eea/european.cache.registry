from flask import current_app

from cache_registry.models import (
    Address,
    BusinessProfile,
    EuLegalRepresentativeCompany,
    Type,
    Undertaking,
    UndertakingBusinessProfile,
    UndertakingTypes,
)
from cache_registry.models import db
from cache_registry.sync import parsers
from cache_registry.sync.auth import patch_users
from cache_registry.sync.bdr import update_bdr_col_name, get_absolute_url
from cache_registry.sync.utils import (
    get_logger,
    get_response,
    update_contact_persons,
)
from instance.settings import FGAS, ODS


def get_latest_undertakings(
    type_url, updated_since=None, page_size=None, id=None, domain=FGAS
):
    """Get latest undertakings from specific API url"""
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

    if page_size:
        params["pageSize"] = page_size
        params["pageNumber"] = 1

    return get_response(url, params)


def patch_undertaking(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get("PATCH_COMPANIES", {})
    if external_id in patch:
        print(f"Patching undertaking: {external_id}")
        data.update(patch[external_id])
    return data


def patch_undertaking_old_gb_represent(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get("PATCH_GB_OLD_REPR", {})
    if external_id in patch:
        represent = data.get("euLegalRepresentativeCompany")
        if not represent:
            print(f"Patching old gb represent on undertaking: {external_id}")
            data.update(patch[external_id])
    return data


def add_updates_log(undertaking, data):

    existing_undertaking_data = f"""
        Organisation ID: {undertaking.external_id}
        Organisation Name: {undertaking.name}
        Organisation Status: {undertaking.status}
        Organisation Domain: {undertaking.domain}
        Organisation type: {undertaking.undertaking_type}
        Organisation Country code: {undertaking.country_code}
        Organisation Country code orig: {undertaking.country_code_orig}
        Organisation vat: {undertaking.vat}
        Organisation check_passed: {undertaking.check_passed}
        Organisation date_created: {undertaking.date_created}
        Organisation date_updated: {undertaking.date_updated}
        Organisation date_created_in_ecr: {undertaking.date_created_in_ecr}
        Organisation date_updated_in_ecr: {undertaking.date_updated_in_ecr}
        Organisation country_history: {[x.code for x in undertaking.country_history]}
        Organisation types: {[x.type for x in undertaking.types]}
        Organisation represent: {undertaking.represent}
        Organisation represent_history: {undertaking.represent_history}
        Organisation businessprofiles: {[x.highleveluses for x in undertaking.businessprofiles]}
    """
    received_undertaking_data = f"Received data: {data}"
    message = f"""
        Undertaking {undertaking.external_id} updated: \n \
        Old data: {existing_undertaking_data} New data: {received_undertaking_data}"
    """
    logger = get_logger("updated")
    logger.info(message)


def update_undertaking(data, check_passed=True):
    """Create or update undertaking from received data"""
    original_data = data.copy()
    represent_changed = False
    # TODO should decide if this should be saved in the DB
    data.pop("registrationId", None)
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
                print(f"Updated collection title for: {undertaking.external_id}")
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
        if (
            business_profile_object
            and business_profile_object not in undertaking.businessprofiles
        ):
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

    update_contact_persons(undertaking, contact_persons)
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
        msg = (
            f"Removing undertaking name: '{undertaking.name}' with id: {undertaking.id}"
        )
        current_app.logger.warning(msg)
        undertaking.represent_history = []
        undertaking.types = []
        undertaking.business_profiles = []
        db.session.commit()
        db.session.delete(undertaking)
    else:
        msg = f"No company with id: {data.get('id')} found in the db"
        current_app.logger.warning(msg)
