from datetime import datetime

from fcs import models
from fcs.models import OldCompany, db


def not_null(func):
    def inner(rc):
        if not rc:
            return None
        return func(rc)

    return inner


def update_obj(obj, d):
    if not d:
        obj = None
    else:
        for name, value in d.iteritems():
            setattr(obj, name, value)
    return obj


def parse_date(date_value):
    return datetime.strptime(date_value, '%d/%m/%Y').date()


def parse_country(country):
    ctr = models.Country.query.filter_by(code=country['code']).first()
    if not ctr:
        ctr = models.Country(**country)
        models.db.session.add(ctr)
    return ctr


def parse_address(address):
    address['zipcode'] = address.pop('zipCode')
    address['country'] = parse_country(address.pop('country'))

    return address


def parse_bp(bp):
    bp['highleveluses'] = ",".join(bp.pop('highLevelUses'))
    return bp


@not_null
def parse_rc(rc):
    rc['vatnumber'] = rc.pop('vatNumber')
    rc['contact_first_name'] = rc.pop('contactPersonFirstName')
    rc['contact_last_name'] = rc.pop('contactPersonLastName')
    rc['contact_email'] = rc.pop('contactPersonEmailAddress')
    rc['address'] = parse_address(rc.pop('address'))
    return rc


def parse_cp_list(cp_list):
    for cp in cp_list:
        cp['username'] = cp.pop('userName')
        cp['first_name'] = cp.pop('firstName')
        cp['last_name'] = cp.pop('lastName')
        cp['email'] = cp.pop('emailAddress')
    return cp_list


def parse_date_for_company(datestr):
    DATE_FORMAT = '%Y/%m/%d %H:%M'
    datestr = datestr[:-11]
    return datetime.strptime(datestr, DATE_FORMAT)


def parse_company(company, obligation):
    country = company.pop('country')
    for f in ('addr_street', 'addr_place1', 'addr_place2', 'addr_postalcode'):
        company.pop(f)
    company['country_code'] = country['code']
    company['external_id'] = company.pop('pk')
    company['date_registered'] = parse_date_for_company(company['date_registered'])
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

