import click

from flask import current_app
from sqlalchemy import func

from cache_registry.models import (
    CountryCodesConversion,
    Licence,
    Undertaking,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import get_absolute_url
from cache_registry.sync.licences_aggregation import (
    aggregate_licence_to_substance,
    aggregate_licences_to_undertakings,
    delete_all_substances_and_licences,
    get_or_create_delivery,
    get_or_create_substance,
)
from cache_registry.sync.utils import get_response


def get_licences(year=2023, page_size=20):
    """Get latest licences from specific API url"""

    url = get_absolute_url("API_URL_ODS", "/latest/licences/")
    params = {"year": year}
    params["pageSize"] = page_size
    params["pageNumber"] = 1

    return get_response(url, params)


def parse_licence(licence, undertaking_id, substance):

    original_country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en)
        == func.lower(licence["organizationCountryName"])
    ).first()
    international_country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en)
        == func.lower(licence["internationalPartyCountryName"])
    ).first()
    if not original_country:
        original_country = ""
        message = (
            f"Country {licence['organizationCountryName']} could not be translated."
        )
        current_app.logger.error(message)
    else:
        original_country = original_country.country_code_alpha2

    if not international_country:
        international_country = ""
        message = f"Country {licence['internationalPartyCountryName']} could not be translated."
        current_app.logger.error(message)
    else:
        international_country = international_country.country_code_alpha2

    licence = {
        "chemical_name": licence["chemicalName"],
        "custom_procedure_name": licence["customProcedureName"],
        "organization_country_name": original_country,
        "organization_country_name_orig": licence["organizationCountryName"],
        "international_party_country_name": international_country,
        "international_party_country_name_orig": licence[
            "internationalPartyCountryName"
        ],
        "total_odp_mass": licence["totalOdpMass"],
        "net_mass": licence["netMass"],
        "licence_state": licence["licenceState"],
        "licence_id": licence["licenceId"],
        "long_licence_number": licence["longLicenceNumber"],
        "template_detailed_use_code": licence["templateDetailedUseCode"],
        "licence_type": licence["licenceType"],
        "mixture_nature_type": licence["mixtureNatureType"],
        "substance_id": substance.id,
        "year": substance.year,
        "updated_since": licence["licenceUpdateDate"],
    }
    licence_object = db.session.query(Licence).filter_by(
        licence_id=licence["licence_id"],
        year=substance.year,
        chemical_name=licence["chemical_name"],
    )
    if licence_object.first():
        licence_object.update(licence)
        licence_object.first().substance = substance
        db.session.add(licence_object.first())
    else:
        licence_object = Licence(**licence, substance=substance)
        db.session.add(licence_object)
    db.session.commit()

    return licence_object


@sync_manager.command("licences")
@click.option("-y", "--year", "year", help="Licences from year x")
@click.option("-p", "--page_size", "page_size", help="Page size")
def licences(year, page_size=200):
    return call_licences(year, page_size)


def call_licences(year, page_size=200):
    data = get_licences(year=year, page_size=page_size)
    companies = aggregate_licences_to_undertakings(data)
    for company, data in companies.items():
        undertaking = Undertaking.query.filter_by(
            external_id=company, domain="ODS"
        ).first()
        delivery_licence = get_or_create_delivery(year, undertaking)
        if (
            delivery_licence.updated_since is None
            or data["updated_since"] > delivery_licence.updated_since
        ):
            delete_all_substances_and_licences(delivery_licence)
            for licence in data["licences"]:
                substance = get_or_create_substance(delivery_licence, licence)
                if not substance:
                    sub_name = f"{licence['chemicalName']}({licence['mixtureNatureType'].lower()})"
                    message = f"Substance {sub_name} could not be translated or Country \
                               code {licence['organizationCountryName']} or Substance \
                               country code {licence['internationalPartyCountryName']} \
                               could not be translated or licence does not have an approved state."
                    current_app.logger.error(message)
                    continue
                parse_licence(licence, undertaking.id, substance)
            aggregate_licence_to_substance(delivery_licence, year)
            delivery_licence.updated_since = data["updated_since"]
            db.session.add(delivery_licence)
            db.session.commit()
    return True
