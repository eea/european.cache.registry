import click
import decimal

from sqlalchemy import func
from flask import current_app

from cache_registry.models import (
    CombinedNomenclature,
    CNQuantity,
    MultiYearLicence,
    MultiYearLicenceAggregated,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.utils import get_response_offset
from cache_registry.sync.commands.multi_year_licences.utils import (
    CUSTOMS_PROCEDURE_NUMBER_TO_LIC_USE_KIND_CONVERSION,
    get_substances_from_cn_code,
)


def get_certex_quantities(
    from_date, to_date, registration_id=None, offset=0, page_size=200
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


def aggregate_quantities_under_cn_codes(data):
    aggregated_data = {}
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
                customs_procedure_number = quantity.get("customsProcedure")
                if cn_code not in aggregated_data[entry["licenceNumber"]]:
                    aggregated_data[entry["licenceNumber"]][cn_code] = {
                        customs_procedure_number: {
                            "reserved_ods_net_mass": decimal.Decimal(0.0),
                            "consumed_ods_net_mass": decimal.Decimal(0.0),
                        }
                    }
                else:
                    if (
                        customs_procedure_number
                        not in aggregated_data[entry["licenceNumber"]][cn_code]
                    ):
                        aggregated_data[entry["licenceNumber"]][cn_code][
                            customs_procedure_number
                        ] = {
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
                    customs_procedure_number
                ]["reserved_ods_net_mass"] += reserved_ods_net_mass
                aggregated_data[entry["licenceNumber"]][cn_code][
                    customs_procedure_number
                ]["consumed_ods_net_mass"] += consumed_ods_net_mass
    return aggregated_data


def get_lic_use_desc_and_lic_type_from_detailed_uses(detailed_uses):
    detailes_uses_data = []
    for detail_use in detailed_uses:
        if not (detail_use.lic_use_desc, detail_use.lic_type) in detailes_uses_data:
            detailes_uses_data.append((detail_use.lic_use_desc, detail_use.lic_type))
    return detailes_uses_data


def remove_certex_data_from_multi_year_licences_aggregated(year):
    # remove existing MultiYearLicenceAggregated entries for the given year created from certex
    MultiYearLicenceAggregated.query.filter_by(
        year=year, created_from_certex=True
    ).delete()
    # remove certex information from MultiYearLicenceAggregated for the given year
    # for entries generated from the MultiYearLicence data
    existing_aggregated_entries = MultiYearLicenceAggregated.query.filter_by(
        year=year, created_from_certex=False, has_certex_data=True
    ).all()
    for entry in existing_aggregated_entries:
        entry.aggregated_reserved_ods_net_mass = 0.0
        entry.aggregated_consumed_ods_net_mass = 0.0
        entry.lic_use_kind = None
        entry.has_certex_data = False
        db.session.add(entry)
    db.session.commit()


def aggregate_certex_quantities_into_multi_year_licences_aggregated(
    cn_quantity_objects, year
):
    remove_certex_data_from_multi_year_licences_aggregated(year)

    # Aggregate CNQuantity data into MultiYearLicenceAggregated
    for cn_quantity in cn_quantity_objects:
        lic_use_kind = CUSTOMS_PROCEDURE_NUMBER_TO_LIC_USE_KIND_CONVERSION.get(
            cn_quantity.customs_procedure
        )
        licence_object = cn_quantity.multi_year_licence
        substances = get_substances_from_cn_code(
            licence_object.id,
            cn_quantity.combined_nomenclature,
            licence_object.substances,
        )
        if not substances:
            current_app.logger.warning(
                f"Licence {licence_object.long_licence_number} has no substances associated with CN code {cn_quantity.combined_nomenclature.code}."
            )
            continue
        detailed_uses_data = get_lic_use_desc_and_lic_type_from_detailed_uses(
            licence_object.detailed_uses
        )
        if len(detailed_uses_data) == 0:
            current_app.logger.warning(
                f"Licence {licence_object.long_licence_number} has no detailed uses associated."
            )
            continue
        elif len(detailed_uses_data) > 1:
            current_app.logger.warning(
                f"Licence {licence_object.long_licence_number} has detailed uses associated with multiple use desc and types."
            )
            continue
        detailed_use_data = detailed_uses_data[0]
        for substance in substances:
            created = False
            multi_year_licence_aggregated = MultiYearLicenceAggregated.query.filter_by(
                multi_year_licence_id=licence_object.id,
                undertaking_id=licence_object.undertaking_id,
                organization_country_name=licence_object.undertaking.country_code,
                s_orig_country_name=licence_object.undertaking.country_code_orig,
                year=year,
                substance=substance.chemical_name,
                lic_use_desc=detailed_use_data[0],
                lic_type=detailed_use_data[1],
                lic_use_kind=lic_use_kind,
            ).first()
            if not multi_year_licence_aggregated:
                # first try to retrieve an existing entry without lic_use_kind. It might be
                # created from multi year licence data and not have lic_use_kind filled in,
                # as that information is not available there.
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
                        lic_use_kind=lic_use_kind,
                        lic_use_desc=detailed_use_data[0],
                        lic_type=detailed_use_data[1],
                        aggregated_reserved_ods_net_mass=cn_quantity.aggregated_reserved_ods_net_mass,
                        aggregated_consumed_ods_net_mass=cn_quantity.aggregated_consumed_ods_net_mass,
                        created_from_certex=True,
                        has_certex_data=True,
                    )
                    created = True
                else:
                    multi_year_licence_aggregated.lic_use_kind = lic_use_kind
            if not created:
                multi_year_licence_aggregated.aggregated_reserved_ods_net_mass += (
                    cn_quantity.aggregated_reserved_ods_net_mass
                )
                multi_year_licence_aggregated.aggregated_consumed_ods_net_mass += (
                    cn_quantity.aggregated_consumed_ods_net_mass
                )
                multi_year_licence_aggregated.has_certex_data = True
            db.session.add(multi_year_licence_aggregated)
    db.session.commit()


@sync_manager.command("certex_quantities")
@click.option("-y", "--year", "year", help="Year for filtering", required=True)
@click.option(
    "-fd", "--from_date", "from_date", help="Start date for filtering (DDMMYYYY)"
)
@click.option("-td", "--to_date", "to_date", help="End date for filtering (DDMMYYYY)")
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
    year, from_date, to_date, registration_id=None, offset=0, page_size=200
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
            from_date = "03032025"
            to_date = "31122025"
        else:
            from_date = f"0101{year}"
            to_date = f"3112{year}"

    # remove existing CNQuantity entries for the given year
    CNQuantity.query.filter_by(year=year).delete()
    db.session.commit()

    # get certex quantities data from the API
    data = get_certex_quantities(from_date, to_date, registration_id, offset, page_size)

    # aggregate quantities under CN codes for each licence
    aggregated_data = aggregate_quantities_under_cn_codes(data)
    cn_quantity_objects = []

    # for each licence and CN code, create or update CNQuantity entries in the database
    for licence_number, cn_codes_data in aggregated_data.items():
        licence_object = MultiYearLicence.query.filter_by(
            long_licence_number=licence_number, status="VALID"
        ).first()
        if not licence_object:
            current_app.logger.warning(
                f"Licence with number {licence_number} not found in the application or not valid."
            )
            continue
        for cn_code, quantities_under_customs_procedure in cn_codes_data.items():
            cn_code_obj = CombinedNomenclature.query.filter(
                func.replace(CombinedNomenclature.code, " ", "") == cn_code
            ).first()
            if not cn_code_obj:
                current_app.logger.warning(
                    f"CN code {cn_code} not found in the application."
                )
                continue
            for (
                customs_procedure_number,
                quantities,
            ) in quantities_under_customs_procedure.items():
                cn_quantity_obj = CNQuantity.query.filter_by(
                    multi_year_licence_id=licence_object.id,
                    combined_nomenclature_id=cn_code_obj.id,
                    customs_procedure=customs_procedure_number,
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
                    customs_procedure=customs_procedure_number,
                    year=2025,
                    aggregated_reserved_ods_net_mass=quantities[
                        "reserved_ods_net_mass"
                    ],
                    aggregated_consumed_ods_net_mass=quantities[
                        "consumed_ods_net_mass"
                    ],
                )
                db.session.add(cn_quantity_obj)
            cn_quantity_objects.append(cn_quantity_obj)
            db.session.commit()

    # using the CNQuantity objects, update multi year licence aggregated
    # entries with certex data
    aggregate_certex_quantities_into_multi_year_licences_aggregated(
        cn_quantity_objects, year
    )
