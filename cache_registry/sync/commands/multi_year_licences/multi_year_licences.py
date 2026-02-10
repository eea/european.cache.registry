import click

from flask import current_app

from cache_registry.models import (
    CombinedNomenclature,
    DetailedUse,
    MultiYearLicence,
    MultiYearLicenceAggregated,
    SubstanceNomenclature,
    Undertaking,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.utils import get_response_offset
from cache_registry.sync.commands.multi_year_licences.utils import (
    get_lic_use_desc_and_lic_type_from_detailed_uses,
    get_substances_from_cn_code,
)


def get_multi_year_licences(
    year,
    registration_id=None,
    long_licence_number=None,
    licence_id=None,
    offset=0,
    page_size=200,
):
    """Get latest multiyearlicences data from the ODS API"""

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
    """
    Receive the following structure:
    [
        {
        "longLicenceNumber": "string",
        "registrationNumId": "string"
        },
        {
        "longLicenceNumber": "string",
        "registrationNumId": "string"
        }...
    ]
    and return a dict of undertakings with the following format:
    {
        "registrationNumId": {
            "licences": [
                {
                    "longLicenceNumber": "string",
                    "registrationNumId": "string"
                },
                {
                    "longLicenceNumber": "string",
                    "registrationNumId": "string"
                }...
            ]
        }
    }
    """
    undertakings = {}
    not_found_undertakings = []
    for licence in data:
        undertaking_obj = Undertaking.query.filter_by(
            registration_id=licence["registrationNumId"], domain="ODS"
        ).first()
        if not undertaking_obj:
            if licence["registrationNumId"] not in not_found_undertakings:
                registration_num_id = licence["registrationNumId"]
                not_found_undertakings.append(registration_num_id)
                message = f"Undertaking {registration_num_id} is not present in the application."
                current_app.logger.error(message)
            continue

        if undertaking_obj.registration_id not in undertakings:
            undertakings[undertaking_obj.registration_id] = {
                "licences": [],
            }
        undertakings[undertaking_obj.registration_id]["licences"].append(licence)
    return undertakings


def parse_cn_codes(licence_object, licence_data):
    licence_object.cn_codes.clear()
    cn_codes = licence_data.get("cnCodes", [])
    for cn_code in cn_codes:
        cn_code_obj = CombinedNomenclature.query.filter_by(
            code=cn_code["code"], description=cn_code["description"]
        ).first()
        if not cn_code_obj:
            current_app.logger.warning(
                f"""Combined Nomenclature code {cn_code['code']}, {cn_code['description']}
                not found in the database.
                """
            )
            continue
        if cn_code_obj not in licence_object.cn_codes:
            licence_object.cn_codes.append(cn_code_obj)
    db.session.add(licence_object)
    db.session.commit()


def parse_substances(licence_object, licence_data):
    licence_object.substances.clear()
    substances = licence_data.get("substances", []) or []
    for substance in substances:
        substance_obj = SubstanceNomenclature.query.filter_by(
            chemical_name=substance["chemicalName"],
            name=substance["name"],
        ).first()
        if not substance_obj:
            current_app.logger.warning(
                f"""Substance {substance['name']} ({substance['chemicalName']})
                not found in the database.
                """
            )
            continue
        if substance_obj not in licence_object.substances:
            licence_object.substances.append(substance_obj)
    db.session.add(licence_object)
    db.session.commit()


def parse_detailed_uses(licence_object, licence_data):
    licence_object.detailed_uses.clear()
    detailed_uses = licence_data.get("detailedUses", []) or []
    for detailed_use in detailed_uses:
        detailed_use_obj = DetailedUse.query.filter_by(
            short_code=detailed_use["shortCode"]
        ).first()
        if not detailed_use_obj:
            current_app.logger.warning(
                f"""Detailed Use with short code {detailed_use['shortCode']}
                not found in the database.
                """
            )
            continue
        if detailed_use_obj not in licence_object.detailed_uses:
            licence_object.detailed_uses.append(detailed_use_obj)
    db.session.add(licence_object)
    db.session.commit()


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

    parse_cn_codes(licence_object, licence_data)
    parse_substances(licence_object, licence_data)
    parse_detailed_uses(licence_object, licence_data)

    return licence_object


def generate_multi_year_licence_aggregated(licence_object, year):
    for cn_code in licence_object.cn_codes:
        substances = get_substances_from_cn_code(
            licence_object.id, cn_code, licence_object.substances
        )
        if not substances:
            continue
        for substance in substances:
            detailed_uses_data = get_lic_use_desc_and_lic_type_from_detailed_uses(
                licence_object
            )
            if len(detailed_uses_data) == 0:
                current_app.logger.warning(
                    f"Licence {licence_object.long_licence_number} has no detailed uses associated or licence_type."
                )
                continue
            elif len(detailed_uses_data) > 1:
                current_app.logger.warning(
                    f"Licence {licence_object.long_licence_number} has detailed uses associated with multiple use desc and types."
                )
                continue
            detailed_use_data = detailed_uses_data[0]
            multi_year_licence_aggregated = MultiYearLicenceAggregated.query.filter_by(
                multi_year_licence_id=licence_object.id,
                undertaking_id=licence_object.undertaking_id,
                organization_country_name=licence_object.undertaking.country_code,
                s_orig_country_name=licence_object.undertaking.country_code_orig,
                year=year,
                substance=substance.chemical_name,
                lic_use_desc=detailed_use_data[0],
                lic_type=detailed_use_data[1],
            ).first()
            if not multi_year_licence_aggregated:
                multi_year_licence_aggregated = MultiYearLicenceAggregated(
                    multi_year_licence_id=licence_object.id,
                    undertaking_id=licence_object.undertaking_id,
                    organization_country_name=licence_object.undertaking.country_code,
                    s_orig_country_name=licence_object.undertaking.country_code_orig,
                    year=year,
                    substance=substance.chemical_name,
                    lic_use_kind=None,
                    lic_use_desc=detailed_use_data[0],
                    lic_type=detailed_use_data[1],
                    aggregated_reserved_ods_net_mass=0.0,  # this will be updated with the Certex data in the next step
                    aggregated_consumed_ods_net_mass=0.0,  # this will be updated with the Certex data in the next step
                )
                db.session.add(multi_year_licence_aggregated)
                db.session.commit()


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
    help="Undertaking registration ID number for filtering",
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
    # get multi year licences data from the ODS API
    data = get_multi_year_licences(
        year, registration_id, long_licence_number, licence_id, offset, page_size
    )

    # aggregate multi year licences under undertakings
    undertakings_with_licences = aggregate_multi_year_licences_to_undertakings(data)
    licence_objects = []

    # create/update MultiYearLicence entries for each licence and collect them in a list to be
    # used for aggregation in the next step
    for company, data in undertakings_with_licences.items():
        undertaking = Undertaking.query.filter_by(
            registration_id=company, domain="ODS"
        ).first()
        for licence in data["licences"]:
            licence_object = parse_multi_year_licence(licence, undertaking.id)
            if licence_object:
                licence_objects.append(licence_object)

    # remove all MultiYearLicenceAggregated entries for the year, as they will
    # be re-aggregated in the next step
    MultiYearLicenceAggregated.query.filter_by(year=year).delete()

    # generate MultiYearLicenceAggregated entries for each licence object
    for licence_object in licence_objects:
        generate_multi_year_licence_aggregated(licence_object, year)
