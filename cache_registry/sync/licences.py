import requests

from flask import current_app
from sqlalchemy import func

from .auth import get_auth
from .bdr import get_absolute_url
from cache_registry.models import DeliveryLicence, Licence, db


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


def parse_licence(licence, undertaking_id, delivery_licence):
    licence = {
        'chemical_name': licence['chemicalName'],
        'custom_procedure_name': licence['customProcedureName'],
        'international_party_country_name': licence['internationalPartyCountryName'],
        'qty_qdp_percentage': licence['qtyQdpPercentage'],
        'qty_percentage': licence['qtyPercentage'],
        'licence_state': licence['licenceState'],
        'licence_id': licence['licenceId'],
        'long_licence_number': licence['longLicenceNumber'],
        'template_detailed_use_code': licence['templateDetailedUseCode'],
        'licence_type': licence['licenceType'],
        'mixture_nature_type': licence['mixtureNatureType'],
        'delivery_id': delivery_licence.id,
        'year': delivery_licence.year
    }
    licence_object = Licence(**licence)
    db.session.add(licence_object)
    db.session.commit()
