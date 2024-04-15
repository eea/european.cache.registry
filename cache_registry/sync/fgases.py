from flask import current_app

from instance.settings import (
    COMPANIES_EXCEPTED_FROM_CHECKS,
    FGAS,
    NOT_OBLIGED_TO_REPORT_FGAS_TYPES,
)
from cache_registry.models import Type


def eea_double_check_fgases(data):
    ok = True

    if not data["businessProfile"]:
        businessprofile = ""
        ok = False
    else:
        businessprofile = data["businessProfile"]["highLevelUses"]

    identifier = f"""
        Organisation ID: {data['id']}
        Organisation status: {data['status']}
        Organisation highLevelUses: {businessprofile}
        Organisation types: {data['types']}
        Organisation contact persons: {data['contactPersons']}
        Organisation domain: {data['domain']}
    """

    country_type = data["address"]["country"]["type"]
    data["address"]["country"]["code"]
    has_eu_legal_rep = data.get("euLegalRepresentativeCompany")

    if str(data["id"]) in COMPANIES_EXCEPTED_FROM_CHECKS:
        message = "Company has been excepted from checks"
        current_app.logger.warning(message + identifier)
        ok = True
        return ok

    if all([country_type in ["NONEU_TYPE", "AMBIGUOUS_TYPE"], not has_eu_legal_rep]):
        message = "NONEU_TYPE and AMBIGOUS_TYPE Companies must have a representative."
        current_app.logger.warning(message + identifier)
        ok = False

    manufacturer = "FGAS_MANUFACTURER_OF_EQUIPMENT_HFCS" in data["types"]
    if all([manufacturer, len(data["types"]) == 1]):
        message = (
            "NONEU_TYPE Equipment manufacturers only, have no reporting" " obligations"
        )
        current_app.logger.warning(message + identifier)
        ok = False

    if not all(("status" in data, data["status"] in ["VALID", "REVISION"])):
        message = "Organisation status differs from VALID or REVISION."
        current_app.logger.warning(message + identifier)
        ok = False

    if data["businessProfile"]:
        if not all(
            [
                high_level_use.startswith("fgas.")
                for high_level_use in data["businessProfile"]["highLevelUses"]
            ]
        ):
            message = "Organisation highLevelUses elements don't start with 'fgas.'"
            current_app.logger.warning(message + identifier)
            ok = False
    else:
        message = "Organisation has no highLevelUses"
        data["businessProfile"] = {"highLevelUses": []}
        current_app.logger.warning(message + identifier)
        ok = False

    if set(data["types"]).issubset(NOT_OBLIGED_TO_REPORT_FGAS_TYPES):
        message = f"Organization types {data['types']} should not report."
        current_app.logger.warning(message + identifier)
        ok = False

    types = [object.type for object in Type.query.filter_by(domain=FGAS)]
    for type in data["types"]:
        if type not in types:
            message = f"Organisation type {type} is not accepted."
            current_app.logger.warning(message + identifier)
            ok = False

    if not data["domain"] == FGAS:
        message = "Organisation domain is not FGAS"
        current_app.logger.warning(message + identifier)
        ok = False

    new_types = ["RECLAIMER_HFCS"]
    for type in data["types"]:
        if type in new_types:
            message = f"NEW TYPE USED for {data['id']}"
            current_app.logger.warning(message + identifier)
    new_high_level_uses = ["fgas.prod-imp-exp.hfcs.exporter", "fgas.prod-imp-exp.hfcs.customs-procedure-release", "fgas.prod-imp-exp.hfcs.customs-others"]
    for high_level_use in data["businessProfile"]["highLevelUses"]:
        if high_level_use in new_high_level_uses:
            message = f"NEW HIGH LEVEL USED for {data['id']}"
            current_app.logger.warning(message + identifier)
    return ok
