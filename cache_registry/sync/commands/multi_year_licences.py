import click

from flask import current_app

from cache_registry.models import (
    CombinedNomenclature,
    MultiYearLicenceDetailedUseLink,
    SubstanceNomenclature,
    DetailedUse,
    MultiYearLicence,
    Undertaking,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.utils import get_response_offset


def get_multi_year_licences(
    year,
    registration_id=None,
    long_licence_number=None,
    licence_id=None,
    offset=0,
    page_size=200,
):
    """Get latest multiyearlicences from specific API url"""

    url = get_absolute_url("API_URL_ODS", "/latest/licences/multiyear/")
    params = {"year": year, "offset": offset, "pageSize": page_size}
    if registration_id:
        params["registrationId"] = registration_id
    if long_licence_number:
        params["longLicenceNumber"] = long_licence_number
    if licence_id:
        params["licenceId"] = licence_id
    return get_response_offset(url, params)


def aggregate_multi_year_licences_to_undertakings(data):
    undertakings = {}
    not_found_undertakings = []
    for licence in data:
        undertaking_obj = Undertaking.query.filter_by(
            registration_id=licence["registrationNumId"], domain="ODS"
        ).first()
        if not undertaking_obj:
            if licence["registrationNumId"] not in not_found_undertakings:
                registration_num_id = licence["registrationNumId"]
                message = f"Undertaking {registration_num_id} is not present in the application."
                current_app.logger.error(message)
                not_found_undertakings.append(licence["registrationNumId"])
            continue
        undertaking = undertakings.get(undertaking_obj.registration_id, None)

        if not undertaking:
            undertakings[undertaking_obj.registration_id] = {
                "licences": [],
            }
        undertaking = undertakings[undertaking_obj.registration_id]
        undertaking["licences"].append(licence)
    return undertakings


def parse_multi_year_licence(licence_data, undertaking_id):

    licence = {
        "long_licence_number": licence_data["longLicenceNumber"],
        "update_date": licence_data["updateDate"],
        "licence_id": licence_data["licenceId"],
        "status": licence_data["status"],
        "status_date": licence_data.pop("statusDate", None),
        "validity_start_date": licence_data["validityStartDate"],
        "validity_end_date": licence_data["validityEndDate"],
        "licence_type": licence_data["licenceType"],
        "substance_mixture": licence_data.get("substanceMixture", None),
    }

    licence_object = (
        db.session.query(MultiYearLicence)
        .filter_by(
            licence_id=licence["licence_id"],
            undertaking_id=undertaking_id,
        )
        .first()
    )
    if licence_object:
        for key, value in licence.items():
            setattr(licence_object, key, value)
        db.session.add(licence_object)
    else:
        licence_object = MultiYearLicence(**licence, undertaking_id=undertaking_id)
        db.session.add(licence_object)
    db.session.commit()

    # CN codes
    licence_object.cn_codes.clear()
    cn_codes = licence_data.get("cnCodes", [])
    for cn_code in cn_codes:
        cn_code_obj = CombinedNomenclature.query.filter_by(code=cn_code["code"]).first()
        if not cn_code_obj:
            cn_code_obj = CombinedNomenclature(
                code=cn_code["code"],
                description=cn_code.get("description", ""),
            )
            db.session.add(cn_code_obj)
            db.session.commit()
        if cn_code_obj not in licence_object.cn_codes:
            licence_object.cn_codes.append(cn_code_obj)
    db.session.add(licence_object)
    db.session.commit()

    # Substances
    licence_object.substances.clear()
    substances = licence_data.get("substances", []) or []
    for substance in substances:
        substance_obj = SubstanceNomenclature.query.filter_by(
            name=substance.get("name", "")
        ).first()
        if not substance_obj:
            substance_obj = SubstanceNomenclature(
                name=substance.get("name", ""),
                chemical_name=substance.get("chemicalName", ""),
            )
            db.session.add(substance_obj)
            db.session.commit()
        if substance_obj not in licence_object.substances:
            licence_object.substances.append(substance_obj)
    db.session.add(licence_object)
    db.session.commit()

    # Detailed Uses
    licence_object.detailed_uses.clear()
    MultiYearLicenceDetailedUseLink.query.filter_by(
        multi_year_licence_id=licence_object.id
    ).delete()
    db.session.commit()
    detailed_uses = licence_data.get("detailedUses", [])
    multi_year_licences_detailed_use_links = []
    for detailed_use in detailed_uses:
        detailed_use_obj = DetailedUse.query.filter_by(
            short_code=detailed_use["shortCode"]
        ).first()
        if not detailed_use_obj:
            detailed_use_obj = DetailedUse(
                short_code=detailed_use["shortCode"],
                code=detailed_use.get("code", ""),
            )
            db.session.add(detailed_use_obj)
            db.session.commit()
        multi_year_licences_detailed_use_links.append(
            MultiYearLicenceDetailedUseLink(
                multi_year_licence_id=licence_object.id,
                detailed_use_id=detailed_use_obj.id,
                valid_until=detailed_use.get("validUntil", None),
            )
        )
    db.session.bulk_save_objects(multi_year_licences_detailed_use_links)
    db.session.commit()
    return licence_object


@sync_manager.command("multi_year_licences")
@click.option(
    "-y",
    "--year",
    "year",
    help="The year during which license were considered 'Valid' at any time",
    required=True,
)
@click.option(
    "-r",
    "--registration_id",
    "registration_id",
    help="Registration ID number for filtering",
)
@click.option(
    "-ln",
    "--long_licence_number",
    "long_licence_number",
    help="Licence number for filtering",
)
@click.option("-l", "--licence_id", "licence_id", help="Licence ID for filtering")
@click.option(
    "-o", "--offset", "offset", help="Offset of rows from the start", default=0
)
@click.option("-p", "--page_size", "page_size", help="Page size", default=200)
def multi_year_licences(
    year,
    registration_id=None,
    long_licence_number=None,
    licence_id=None,
    offset=0,
    page_size=200,
):
    return call_multi_year_licences(
        year, registration_id, long_licence_number, licence_id, offset, page_size
    )


def call_multi_year_licences(
    year,
    registration_id=None,
    long_licence_number=None,
    licence_id=None,
    offset=0,
    page_size=200,
):
    data = get_multi_year_licences(
        year, registration_id, long_licence_number, licence_id, offset, page_size
    )
    undertakings_with_licences = aggregate_multi_year_licences_to_undertakings(data)
    for company, data in undertakings_with_licences.items():
        undertaking = Undertaking.query.filter_by(
            registration_id=company, domain="ODS"
        ).first()
        for licence in data["licences"]:
            parse_multi_year_licence(licence, undertaking.id)
