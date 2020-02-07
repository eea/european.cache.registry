import hashlib
import json
import requests


from flask import current_app
from sqlalchemy import func

from .auth import get_auth
from .bdr import get_absolute_url
from cache_registry.models import (
    DeliveryLicence,
    Licence,
    CountryCodesConversion,
    HashLicencesJson,
    SubstanceNameConversion,
    LicenceDetailsConverstion,
    Substance,
    Undertaking,
    db,
)

def delete_all_substances_and_licences(delivery_licence):
    substances = Substance.query.filter_by(deliverylicence=delivery_licence)
    substances.delete()
    db.session.commit()

def get_or_create_delivery(year, undertaking):
    delivery = DeliveryLicence.query.filter_by(year=year, undertaking=undertaking).first()
    if delivery:
        return delivery
    delivery = DeliveryLicence(year=year, undertaking=undertaking)
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
        current_app.logger.error(message)
    else:
        original_country = original_country.country_code_alpha2

    if not international_country:
        international_country = ''
        message = 'Country {} could not be translated.'.format(licence['internationalPartyCountryName'])
        current_app.logger.error(message)
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
    licence_object = db.session.query(Licence).filter_by(licence_id=licence['licence_id'],year=substance.year)
    if licence_object.first():
        licence_object.update(licence)
    else:
        licence_object = Licence(**licence)
        db.session.add(licence_object)
    db.session.commit()

    return licence_object

def get_or_create_substance(delivery_licence, licence):
    if licence['mixtureNatureType'].lower() != 'virgin':
        ec_substance_name = "{} (non-virgin)".format(licence['chemicalName'])
    else:
        ec_substance_name = "{} ({})".format(licence['chemicalName'], licence['mixtureNatureType'].lower())
    substance_conversion = SubstanceNameConversion.query.filter_by(ec_substance_name=ec_substance_name).first()
    if not substance_conversion:
        return None
    country = CountryCodesConversion.query.filter_by(country_name_short_en=licence['organizationCountryName']).first()
    if not country:
        return None
    licence_details = LicenceDetailsConverstion.query.filter_by(
        template_detailed_use_code=licence['templateDetailedUseCode']).first()

    substance = Substance.query.filter_by(
        substance=substance_conversion.corrected_name,
        organization_country_name=country.country_code_alpha2,
        lic_use_desc=licence_details.lic_use_desc,
        deliverylicence=delivery_licence,
        year=delivery_licence.year,
        ).first()
    if not substance:
        substance = Substance(
            substance=substance_conversion.corrected_name,
            deliverylicence=delivery_licence,
            organization_country_name=country.country_code_alpha2,
            year=delivery_licence.year,
            lic_use_kind=licence_details.lic_use_kind,
            lic_use_desc=licence_details.lic_use_desc,
            lic_type=licence_details.lic_type,
            quantity=0,
            )
        db.session.add(substance)
        db.session.commit()
    return substance


def aggregate_licence_to_substance(delivery_licence, year):
    substances = Substance.query.filter_by(year=year, deliverylicence=delivery_licence)
    for substance in substances:
        substance.quantity = sum([licence.qty_percentage for licence in substance.licences.all()])
        db.session.add(substance)
        db.session.commit()

def aggregate_licences_to_undertakings(data):
    undertakings = {}
    not_found_undertakings = []
    for licence in data:
        undertaking_obj = Undertaking.query.filter_by(name=licence['organizationName'], domain='ODS').first()
        if not undertaking_obj:
            if licence['organizationName'] not in not_found_undertakings:
                message = 'Undertaking {} is not present in the application.'.format(licence['organizationName'])
                current_app.logger.error(message)
                not_found_undertakings.append(licence['organizationName'])
            continue
        undertaking = undertakings.get(undertaking_obj.external_id, None)
        if not undertaking:
            undertakings[undertaking_obj.external_id] = {"updated_since": None, "licences": []}
            undertaking = undertakings[undertaking_obj.external_id]
        undertaking['licences'].append(licence)
    return undertakings

def licences_json_was_updated(data, year):
    json_data = json.dumps(data, sort_keys=True, indent=2)
    hash_value = hashlib.md5(json_data.encode("utf-8")).hexdigest()
    hash_object = HashLicencesJson.query.filter_by(year=year).first()
    if not hash_object:
        hash_object = HashLicencesJson(year=year, hash_value=hash_value)
        db.session.add(hash_object)
        db.session.commit()
        return True
    if hash_object.hash_value != hash_value:
        hash_object.hash_value =  hash_value
        db.session.add(hash_object)
        db.session.commit()
        return True
    return False
