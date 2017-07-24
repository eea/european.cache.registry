from datetime import datetime

from fcs import models


def not_null(func):
    def inner(rc):
        if not rc:
            return None
        return func(rc)

    return inner


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
