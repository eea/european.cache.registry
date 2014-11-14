from datetime import datetime
import requests
from flask.ext.script import Manager
from flask import current_app
from fcs.models import Undertaking, db, Address, Country, BusinessProfile

sync_manager = Manager()


class Unauthorized(Exception):
    pass


class InvalidResponse(Exception):
    pass


def get_absolute_url(url):
    return current_app.config['API_URL'] + url


def get_auth():
    return (
        current_app.config.get('API_USER', 'user'),
        current_app.config.get('API_PASSWORD', 'pass'),
    )


def get_latest_undertakings(updated_since=None):
    auth = get_auth()
    url = get_absolute_url('/latest/fgasundertakings/')
    if updated_since:
        updated_since = updated_since.strftime('%d/%m/%Y')
        params = {'updatedSince': updated_since}
    else:
        params = {}

    response = requests.get(url, params=params, auth=auth)
    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    with open('instance/test.json', 'r') as data_file:
        import json
        data = json.load(data_file)
        return data
    #return response.json()


def update_obj(obj, d):
    for name, value in d.iteritems():
        setattr(obj, name, value)
    return obj


def parse_date(date_value):
    return datetime.strptime(date_value, '%d/%m/%Y').date()


def parse_country(country):
    ctr = Country.query.filter_by(code=country['code']).first()
    if not ctr:
        ctr = Country(**country)
        db.session.add(ctr)
    return ctr


def parse_address(address):
    address['zipcode'] = address.pop('zipCode')
    address['country'] = parse_country(address.pop('country'))
    return address


def parse_bp(bp):
    bp['highleveluses'] = ",".join(bp.pop('highLevelUses'))
    return bp


def parse_undertaking(data):
    address = parse_address(data.pop('address'))
    business_profile = parse_bp(data.pop('businessProfile'))
    contact_persons = data.pop('contactPersons') # TODO: parse and add
    represent = data.pop('euLegalRepresentativeCompany') # TODO parse and add

    data['types'] = ','.join(data['types'])
    data['external_id'] = data.pop('id')
    data['date_created'] = parse_date(data.pop('dateCreated'))
    data['date_updated'] = parse_date(data.pop('dateUpdated'))
    data.pop('@type', None)

    undertaking = (
        Undertaking.query
        .filter_by(external_id=data['external_id'])
        .first()
    )

    if not undertaking:
        undertaking = Undertaking(**data)

    if not undertaking.address:
        addr = Address(**address)
        db.session.add(addr)
        undertaking.address = addr
    else:
        update_obj(undertaking.address, address)

    if not undertaking.businessprofile:
        bp = BusinessProfile(**business_profile)
        db.session.add(bp)
        undertaking.businessprofile = bp
    else:
        update_obj(undertaking.businessprofile, business_profile)

    db.session.add(undertaking)


@sync_manager.command
def test():
    import pprint

    res = get_latest_undertakings()
    pprint.pprint(res)

    for u in res:
        parse_undertaking(u)

    db.session.commit()
