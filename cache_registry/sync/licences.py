import requests

from flask import current_app
from sqlalchemy import func

from .auth import get_auth
from .bdr import get_absolute_url
from cache_registry.models import HistoryLicence, Licence, db


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


def parse_licence(licence, undertaking_id, delivery_name, year):
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
        'undertaking_id': undertaking_id,
        'name': delivery_name,
        'year': year
    }
    licence_object = Licence(**licence)
    db.session.add(licence_object)
    db.session.commit()


def move_licence_history(undertaking):
    licences = undertaking.licences
    for licence in licences:
        history_licence = HistoryLicence.query.filter_by(name=licence.name, year=licence.year).first()
        history_order = HistoryLicence.query.filter_by(year=licence.year).order_by(HistoryLicence.order.desc()).first()
        if not history_order:
            order = 1
        else:
            order = history_order.order + 1
        if not history_licence:
            history_licence = HistoryLicence(
                name=licence.name, year=licence.year,
                order=order, undertaking_id=licence.undertaking_id
            )
            db.session.add(history_licence)
            db.session.commit()
        licence.history_licence_id = history_licence.id
        licence.undertaking = None
        licence.undertaking_id = None
        db.session.add(licence)
    db.session.commit()
