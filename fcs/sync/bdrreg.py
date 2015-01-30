import requests
from datetime import datetime
from flask import current_app
from fcs.sync import sync_manager, InvalidResponse, Unauthorized
from fcs.sync.utils import update_obj
from fcs.models import db, OldCompany


def get_obligations():
    if current_app.config.get('GET_ALL_INTERESTING_OBLIGATIONS', '') is True:
        return ['fgases', 'mercury', 'vans', 'cars', 'ods']
    return ['fgases']


def get_absolute_url(url):
    return current_app.config['BDR_API_URL'] + url


def get_auth():
    return current_app.config.get('BDR_API_KEY', '')


def get_old_companies(obligation):
    auth = get_auth()
    url = get_absolute_url('/company/obligation/{0}/'.format(obligation))
    params = {'apikey': auth}
    ssl_verify = current_app.config['HTTPS_VERIFY']

    response = requests.get(url, params=params, verify=ssl_verify)
    if response.status_code in (401, 403):
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    return response.json()


def parse_date(datestr):
    DATE_FORMAT = '%Y/%m/%d %H:%M'
    datestr = datestr[:-11]
    return datetime.strptime(datestr, DATE_FORMAT)


def parse_company(company, obligation):
    country = company.pop('country')
    for f in ('addr_street', 'addr_place1', 'addr_place2', 'addr_postalcode'):
        company.pop(f)
    company['country_code'] = country['code']
    company['external_id'] = company.pop('pk')
    company['date_registered'] = parse_date(company['date_registered'])
    company['obligation'] = obligation

    oldcompany = (
        OldCompany.query.filter_by(external_id=company['external_id']).first()
    )
    if oldcompany:
        update_obj(oldcompany, company)
    else:
        oldcompany = OldCompany(**company)
        db.session.add(oldcompany)
    return company


@sync_manager.command
def bdr():
    companies = []
    for obl in get_obligations():
        print "Getting obligation: ", obl
        companies = get_old_companies(obl)
        print len([parse_company(c, obl) for c in companies]), "values"
    db.session.commit()
