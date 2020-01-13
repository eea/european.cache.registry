import requests

from flask import current_app
from sqlalchemy import func

from .auth import get_auth
from .bdr import get_absolute_url
from cache_registry.models import (
    DeliveryLicence,
    Licence,
    CountryCodesConversion,
    SubstanceNameConversion,
    LicenceDetailsConverstion,
    Substance,
    db,
)


def check_if_delivery_exists(year, delivery_name):
    delivery =  DeliveryLicence.query.filter_by(year=year, name=delivery_name).first()
    if delivery:
        return True

def get_new_delivery_order(year, undertaking_id):
    delivery_order = DeliveryLicence.query.filter_by(
    year=year,
    undertaking_id=undertaking_id).order_by(DeliveryLicence.order.desc()).first()
    if not delivery_order:
        return 1
    return delivery_order.order + 1

def get_or_create_delivery(year, delivery_name, undertaking_id):
    delivery = DeliveryLicence.query.filter_by(year=year, name=delivery_name).first()
    if delivery:
        return delivery

    histories =  DeliveryLicence.query.filter_by(
        year=year, undertaking_id=undertaking_id, current=True)
    for delivery in histories:
        delivery.current = False
        db.session.add(delivery)
        db.session.commit()

    delivery = DeliveryLicence(
        order=get_new_delivery_order(year, undertaking_id),
        current=True,
        name=delivery_name,
        year=year,
        undertaking_id=undertaking_id
    )

    db.session.add(delivery)
    db.session.commit()
    return delivery



def get_licences(year=2017, page_size=20):
    """ Get latest licences from specific API url """
    auth = get_auth('API_USER', 'API_PASSWORD')
    url = get_absolute_url('API_URL', '/latest/licences/')

    params = {'year': year}
    
    headers = dict(zip(('user', 'password'), auth))
    ssl_verify = current_app.config['HTTPS_VERIFY']

    params['pageSize'] = page_size
    params['pageNumber'] = 1

    response = requests.get(url, params=params, headers=headers,
                            verify=ssl_verify)

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()


    no_of_pages = int(response.headers['numberOfPages'])
    response_json = response.json()

    for page_number in range(2, no_of_pages + 1):
        params['pageNumber'] = page_number
        response = requests.get(url, params=params,
                                headers=headers, verify=ssl_verify)
        if response.status_code != 200:
            raise InvalidResponse()
        response_json += response.json()
    return response_json


def parse_licence(licence, undertaking_id, substance):

    original_country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en) == func.lower(licence['organizationCountryName'])).first()
    international_country = CountryCodesConversion.query.filter(
        func.lower(CountryCodesConversion.country_name_short_en) == func.lower(licence['internationalPartyCountryName'])).first()
    if not original_country:
        original_country = ''
        message = 'Country {} could not be translated.'.format(licence['organizationCountryName'])
        current_app.logger.warning(message)
    else:
        original_country = original_country.country_code_alpha2

    if not international_country:
        international_country = ''
        message = 'Country {} could not be translated.'.format(licence['internationalPartyCountryName'])
        current_app.logger.warning(message)
    else:
        international_country = international_country.country_code_alpha2

    licence = {
        'chemical_name': licence['chemicalName'],
        'custom_procedure_name': licence['customProcedureName'],
        'organization_country_name': original_country,
        'organization_country_name_orig': licence['organizationCountryName'],
        'international_party_country_name': international_country,
        'international_party_country_name_orig': licence['internationalPartyCountryName'],
        'qty_qdp_percentage': licence['qtyQdpPercentage'],
        'qty_percentage': licence['qtyPercentage'],
        'licence_state': licence['licenceState'],
        'licence_id': licence['licenceId'],
        'long_licence_number': licence['longLicenceNumber'],
        'template_detailed_use_code': licence['templateDetailedUseCode'],
        'licence_type': licence['licenceType'],
        'mixture_nature_type': licence['mixtureNatureType'],
        'substance_id': substance.id,
        'year': substance.year
    }
    licence_object = Licence(**licence)
    db.session.add(licence_object)
    db.session.commit()

    return licence_object

def get_substance(delivery_licence, licence):
    ec_substance_name = "{} ({})".format(licence['chemicalName'], licence['mixtureNatureType'].lower())
    substance_conversion = SubstanceNameConversion.query.filter_by(ec_substance_name=ec_substance_name).first()
    if not substance_conversion:
        return None
    substance = Substance.query.filter_by(substance=substance_conversion.corrected_name,
                                          deliverylicence=delivery_licence).first()
    if not substance:
        licence_details = LicenceDetailsConverstion.query.filter_by(
            template_detailed_use_code=licence['templateDetailedUseCode']).first()

        substance = Substance(
            substance=substance_conversion.corrected_name,
            deliverylicence=delivery_licence,
            year=delivery_licence.year,
            lic_use_kind=licence_details.lic_use_kind,
            lic_use_desc=licence_details.lic_use_desc,
            lic_type=licence_details.lic_type,
            quantity=0,
            )
        db.session.add(substance)
        db.session.commit()
    return substance


def aggregate_licence_to_substance(substance, licence):
    substance.quantity = substance.quantity + licence.qty_percentage
    db.session.add(substance)
    db.session.commit()
