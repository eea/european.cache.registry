import click
import decimal

from flask import current_app

from cache_registry.models import (
    CombinedNomenclature,
    CNQuantity,
    #     MultiYearLicenceDetailedUseLink,
    #     SubstanceNomenclature,
    #     DetailedUse,
    MultiYearLicence,
    #     Undertaking,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.utils import get_response_offset


# def aggregate_multi_year_licences_to_undertakings(data):
#     undertakings = {}
#     not_found_undertakings = []
#     for licence in data:
#         undertaking_obj = Undertaking.query.filter_by(
#             registration_id=licence["registrationNumId"], domain="ODS"
#         ).first()
#         if not undertaking_obj:
#             if licence["registrationNumId"] not in not_found_undertakings:
#                 registration_num_id = licence["registrationNumId"]
#                 message = f"Undertaking {registration_num_id} is not present in the application."
#                 current_app.logger.error(message)
#                 not_found_undertakings.append(licence["registrationNumId"])
#             continue
#         undertaking = undertakings.get(undertaking_obj.registration_id, None)

#         if not undertaking:
#             undertakings[undertaking_obj.registration_id] = {
#                 "licences": [],
#             }
#         undertaking = undertakings[undertaking_obj.registration_id]
#         undertaking["licences"].append(licence)
#     return undertakings


# def parse_multi_year_licence(licence_data, undertaking_id):

#     licence = {
#         "long_licence_number": licence_data["longLicenceNumber"],
#         "update_date": licence_data["updateDate"],
#         "licence_id": licence_data["licenceId"],
#         "status": licence_data["status"],
#         "status_date": licence_data.pop("statusDate", None),
#         "validity_start_date": licence_data["validityStartDate"],
#         "validity_end_date": licence_data["validityEndDate"],
#         "licence_type": licence_data["licenceType"],
#         "substance_mixture": licence_data.get("substanceMixture", None),
#     }

#     licence_object = (
#         db.session.query(MultiYearLicence)
#         .filter_by(
#             licence_id=licence["licence_id"],
#             undertaking_id=undertaking_id,
#         )
#         .first()
#     )
#     if licence_object:
#         for key, value in licence.items():
#             setattr(licence_object, key, value)
#         db.session.add(licence_object)
#     else:
#         licence_object = MultiYearLicence(**licence, undertaking_id=undertaking_id)
#         db.session.add(licence_object)
#     db.session.commit()

#     # CN codes
#     licence_object.cn_codes.clear()
#     cn_codes = licence_data.get("cnCodes", [])
#     for cn_code in cn_codes:
#         cn_code_obj = CombinedNomenclature.query.filter_by(code=cn_code["code"]).first()
#         if not cn_code_obj:
#             cn_code_obj = CombinedNomenclature(
#                 code=cn_code["code"],
#                 description=cn_code.get("description", ""),
#             )
#             db.session.add(cn_code_obj)
#             db.session.commit()
#         if cn_code_obj not in licence_object.cn_codes:
#             licence_object.cn_codes.append(cn_code_obj)
#     db.session.add(licence_object)
#     db.session.commit()

#     # Substances
#     licence_object.substances.clear()
#     substances = licence_data.get("substances", []) or []
#     for substance in substances:
#         substance_obj = SubstanceNomenclature.query.filter_by(
#             name=substance.get("name", "")
#         ).first()
#         if not substance_obj:
#             substance_obj = SubstanceNomenclature(
#                 name=substance.get("name", ""),
#                 chemical_name=substance.get("chemicalName", ""),
#             )
#             db.session.add(substance_obj)
#             db.session.commit()
#         if substance_obj not in licence_object.substances:
#             licence_object.substances.append(substance_obj)
#     db.session.add(licence_object)
#     db.session.commit()

#     # Detailed Uses
#     licence_object.detailed_uses.clear()
#     MultiYearLicenceDetailedUseLink.query.filter_by(
#         multi_year_licence_id=licence_object.id
#     ).delete()
#     db.session.commit()
#     detailed_uses = licence_data.get("detailedUses", [])
#     multi_year_licences_detailed_use_links = []
#     for detailed_use in detailed_uses:
#         detailed_use_obj = DetailedUse.query.filter_by(
#             short_code=detailed_use["shortCode"]
#         ).first()
#         if not detailed_use_obj:
#             detailed_use_obj = DetailedUse(
#                 short_code=detailed_use["shortCode"],
#                 code=detailed_use.get("code", ""),
#             )
#             db.session.add(detailed_use_obj)
#             db.session.commit()
#         multi_year_licences_detailed_use_links.append(
#             MultiYearLicenceDetailedUseLink(
#                 multi_year_licence_id=licence_object.id,
#                 detailed_use_id=detailed_use_obj.id,
#                 valid_until=detailed_use.get("validUntil", None),
#             )
#         )
#     db.session.bulk_save_objects(multi_year_licences_detailed_use_links)
#     db.session.commit()
#     return licence_object


# def get_multi_year_licences(
#     year,
#     registration_id=None,
#     long_licence_number=None,
#     licence_id=None,
#     offset=0,
#     page_size=200,
# ):
#     """Get latest multiyearlicences from specific API url"""

#     url = get_absolute_url("API_URL_ODS", "/latest/licences/multiyear/")
#     params = {"year": year, "offset": offset, "pageSize": page_size}
#     if registration_id:
#         params["registrationId"] = registration_id
#     if long_licence_number:
#         params["longLicenceNumber"] = long_licence_number
#     if licence_id:
#         params["licenceId"] = licence_id
#     return get_response_offset(url, params)


def get_certex_quantities(
    from_date,
    to_date,
    registration_id=None,
    offset=0,
    page_size=200,
):
    """Get certex quantities from specific API url"""

    url = get_absolute_url("API_URL_ODS", "/latest/certex-quantities/")
    params = {
        "fromDate": from_date,
        "toDate": to_date,
        "offset": offset,
        "pageSize": page_size,
    }
    if registration_id:
        params["registrationId"] = registration_id
    return get_response_offset(url, params)


@sync_manager.command("certex_quantities")
@click.option(
    "-y",
    "--year",
    "year",
    help="Year for filtering",
    required=True,
)
@click.option(
    "-fd",
    "--from_date",
    "from_date",
    help="Start date for filtering (DDMMYYYY)",
)
@click.option(
    "-td",
    "--to_date",
    "to_date",
    help="End date for filtering (DDMMYYYY)",
)
@click.option(
    "-r",
    "--registration_id",
    "registration_id",
    help="Undertaking registration ID number for filtering",
)
@click.option(
    "-o", "--offset", "offset", help="Offset of rows from the start", default=0
)
@click.option("-p", "--page_size", "page_size", help="Page size", default=200)
def certex_quantities(
    year,
    from_date,
    to_date,
    registration_id=None,
    offset=0,
    page_size=200,
):
    return call_certex_quantities(
        year, from_date, to_date, registration_id, offset, page_size
    )


def call_certex_quantities(
    year,
    from_date,
    to_date,
    registration_id=None,
    offset=0,
    page_size=200,
):
    if not from_date or not to_date:
        if int(year) == 2025:
            from_date = "01032025"
            to_date = "31122025"
        else:
            from_date = f"0101{year}"
            to_date = f"3112{year}"

    CNQuantity.query.filter_by(year=year).delete()
    db.session.commit()

    data = get_certex_quantities(from_date, to_date, registration_id, offset, page_size)
    aggregated_data = aggregate_quantities_under_cn_codes(data)
    for licence_number, cn_codes_data in aggregated_data.items():
        licence_object = MultiYearLicence.query.filter_by(
            long_licence_number=licence_number, status="VALID"
        ).first()
        if not licence_object:
            current_app.logger.warning(
                f"Licence with number {licence_number} not found in the application."
            )
            continue
        for cn_code, quantities in cn_codes_data.items():
            cn_code_obj = CombinedNomenclature.query.filter_by(code=cn_code).first()
            if not cn_code_obj:
                cn_code_obj = CombinedNomenclature(
                    code=cn_code,
                    description="",
                )
                db.session.add(cn_code_obj)
                db.session.commit()
            cn_quantity_obj = CNQuantity.query.filter_by(
                multi_year_licence_id=licence_object.id,
                combined_nomenclature_id=cn_code_obj.id,
                undertaking_id=licence_object.undertaking_id,
                year=2025,
            ).first()
            if cn_quantity_obj:
                cn_quantity_obj.aggregated_reserved_ods_net_mass += quantities[
                    "reserved_ods_net_mass"
                ]
                cn_quantity_obj.aggregated_consumed_ods_net_mass += quantities[
                    "consumed_ods_net_mass"
                ]
                db.session.add(cn_quantity_obj)
            else:
                cn_quantity_obj = CNQuantity(
                    multi_year_licence_id=licence_object.id,
                    combined_nomenclature_id=cn_code_obj.id,
                    undertaking_id=licence_object.undertaking_id,
                    year=2025,
                    aggregated_reserved_ods_net_mass=quantities[
                        "reserved_ods_net_mass"
                    ],
                    aggregated_consumed_ods_net_mass=quantities[
                        "consumed_ods_net_mass"
                    ],
                )
                db.session.add(cn_quantity_obj)
            db.session.commit()


def aggregate_quantities_under_cn_codes(data):
    aggregated_data = {}
    aggregated_ghost_data = {}
    for entry in data:
        if entry["ghostLicenceNumber"]:
            current_app.logger.warning(
                f"Licence {entry['licenceNumber']} has ghost licence number {entry['ghostLicenceNumber']}"
            )
            continue
        if entry["licenceNumber"] not in aggregated_data:
            # for each licence number key, create a dict with cn_codes as keys
            # and reserved/consumed masses as values
            aggregated_data[entry["licenceNumber"]] = {}
        for mrn in entry.get("mrns", []):
            for quantity in mrn.get("quantities", []):
                cn_code = quantity["cnCode"]

                if cn_code not in aggregated_data[entry["licenceNumber"]]:
                    aggregated_data[entry["licenceNumber"]][cn_code] = {
                        "reserved_ods_net_mass": decimal.Decimal(0.0),
                        "consumed_ods_net_mass": decimal.Decimal(0.0),
                    }
                reserved_ods_net_mass = decimal.Decimal(
                    quantity.get("reservedOdsNetMass", decimal.Decimal(0.0))
                    or decimal.Decimal(0.0)
                )
                consumed_ods_net_mass = decimal.Decimal(
                    quantity.get("consumedOdsNetMass", decimal.Decimal(0.0))
                    or decimal.Decimal(0.0)
                )
                aggregated_data[entry["licenceNumber"]][cn_code][
                    "reserved_ods_net_mass"
                ] += reserved_ods_net_mass
                aggregated_data[entry["licenceNumber"]][cn_code][
                    "consumed_ods_net_mass"
                ] += consumed_ods_net_mass
    return aggregated_data
