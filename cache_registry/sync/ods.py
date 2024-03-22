from flask import current_app
from instance.settings import (
    ODS,
    NOT_OBLIGED_TO_REPORT,
    NO_HIGHLEVEL_TYPES,
    NOT_OBLIGED_TO_REPORT_ODS_TYPES,
    COMPANIES_EXCEPTED_FROM_CHECKS,
)


from cache_registry.models import Type, BusinessProfile


def eea_double_check_ods(data):
    identifier = f"""
        Organisation ID: {data['id']}
        Organisation status: {data['status']}
        Organisation highLevelUses: {data['businessProfile']['highLevelUses']}
        Organisation types: {data['types']}
        Organisation contact persons: {data['contactPersons']}
        Organisation domain: {data['domain']}
    """

    required_fields = [
        "@type",
        "id",
        "name",
        "address",
        "phone",
        "domain",
        "dateCreated",
        "dateUpdated",
        "status",
        "eoriNumber",
        "types",
        "businessProfile",
    ]
    required_fields_country = ["code", "name", "type"]
    required_fields_user = ["userName", "firstName", "lastName", "emailAddress"]
    ok = True

    if str(data["id"]) in COMPANIES_EXCEPTED_FROM_CHECKS:
        message = "Company has been excepted from checks"
        current_app.logger.warning(message + identifier)
        ok = True
        return ok

    for field in required_fields:
        if not all((field in data, data[field])):
            message = f"Organisation {field} field is missing."
            current_app.logger.warning(message + identifier)
            ok = False

    if data["@type"] != "ODSUndertaking":
        message = "Organisation type is not ODSUndertaking."
        current_app.logger.warning(message + identifier)
        ok = False

    if not data["domain"] == ODS:
        message = "Organisation domain is not ODS."
        current_app.logger.warning(message + identifier)
        ok = False

    if data["status"] not in ["VALID", "REVISION"]:
        message = "Organisation status differs from VALID or REVISION."
        current_app.logger.warning(message + identifier)
        ok = False

    if not all(("country" in data["address"], data["address"]["country"])):
        message = "Organisation address country is missing."
        current_app.logger.warning(message + identifier)
        ok = False

    country = data["address"]["country"]
    for field in required_fields_country:
        if not all((field in country, country[field])):
            message = f"Organisation country {field} is missing."
            current_app.logger.warning(message + identifier)
            ok = False

    if country["type"] not in ["EU_TYPE", "AMBIGUOUS_TYPE"]:
        message = "Organisation country type is not EU_TYPE."
        current_app.logger.warning(message + identifier)
        ok = False

    for user in data["contactPersons"]:
        for field in required_fields_user:
            if not all((field in user, user[field])):
                message = f"Organisation user {field} is missing."
                current_app.logger.warning(message + identifier)
                ok = False

    types = [object.type for object in Type.query.filter_by(domain=ODS)]
    for type in data["types"]:
        if type not in types:
            message = f"Organisation type {type} is not accepted."
            current_app.logger.warning(message + identifier)
            ok = False

    businessprofiles = [
        object.highleveluses for object in BusinessProfile.query.filter_by(domain=ODS)
    ]
    obliged_to_report = False

    high_level_uses_set = set(data["businessProfile"]["highLevelUses"])

    if set(data["types"]).issubset(NOT_OBLIGED_TO_REPORT_ODS_TYPES):
        message = f"Organization types {data['types']} should not report."
        current_app.logger.warning(message + identifier)
        ok = False

    if not (high_level_uses_set or set(data["types"]) & NO_HIGHLEVEL_TYPES):
        message = "Organisation high level uses are missing."
        current_app.logger.warning(message + identifier)
        ok = False

    for high_level_use in data["businessProfile"]["highLevelUses"]:
        if high_level_use not in businessprofiles:
            message = f"Organisation highlevel use {high_level_use} is not accepted."
            current_app.logger.warning(message + identifier)
            ok = False
        elif high_level_use not in NOT_OBLIGED_TO_REPORT:
            high_level_uses_set.remove(high_level_use)
            obliged_to_report = True

    if not obliged_to_report and high_level_uses_set:
        high_lvl_uses_text = ", ".join(high_level_uses_set)
        message = f"Organisations with highlevel uses {high_lvl_uses_text} should not be reported."
        current_app.logger.warning(message + identifier)
        ok = False

    return ok
