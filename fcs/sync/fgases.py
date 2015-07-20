from datetime import datetime, timedelta

import requests

from sqlalchemy import desc
from flask import current_app

from fcs.models import (
    Undertaking, db, Address, Country, BusinessProfile, User,
    EuLegalRepresentativeCompany, OrganizationLog,
)
from fcs.sync import sync_manager, Unauthorized, InvalidResponse
from fcs.sync.utils import update_obj


def not_null(func):
    def inner(rc):
        if not rc:
            return None
        return func(rc)

    return inner


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

    headers = dict(zip(('user', 'password'), auth))
    ssl_verify = current_app.config['HTTPS_VERIFY']
    response = requests.get(url, params=params, headers=headers,
                            verify=ssl_verify)

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    return response.json()


def patch_users(external_id, users):
    """ Patch the list of contact persons
    """
    external_id = str(external_id)
    patch = current_app.config.get('PATCH_USERS', {})
    if external_id in patch:
        print("Patching company: {}".format(external_id))
        users.extend(patch[external_id])
    return users


def patch_undertaking(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get('PATCH_COMPANIES', {})
    if external_id in patch:
        print("Patching undertaking: {}".format(external_id))
        data.update(patch[external_id])
    return data


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


def parse_undertaking(data):
    data = patch_undertaking(data['id'], data)
    address = parse_address(data.pop('address'))
    business_profile = parse_bp(data.pop('businessProfile'))
    contact_persons = parse_cp_list(data.pop('contactPersons'))
    represent = parse_rc(data.pop('euLegalRepresentativeCompany'))

    contact_persons = patch_users(data['id'], contact_persons)
    data['types'] = ','.join(data['types'])
    data['external_id'] = data.pop('id')
    data['date_created'] = parse_date(data.pop('dateCreated'))
    data['date_updated'] = parse_date(data.pop('dateUpdated'))
    data['undertaking_type'] = data.pop('@type', None)

    undertaking = (
        Undertaking.query
        .filter_by(external_id=data['external_id'])
        .first()
    )

    if not undertaking:
        undertaking = Undertaking(**data)
    else:
        update_obj(undertaking, data)

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

    if not represent:
        old_represent = undertaking.represent
        undertaking.represent = None
        if old_represent:
            db.session.delete(old_represent)
    else:
        address = represent.pop('address')
        if not undertaking.represent:
            addr = Address(**address)
            db.session.add(addr)
            r = EuLegalRepresentativeCompany(**represent)
            db.session.add(r)

            undertaking.represent = r
            undertaking.represent.address = addr
        else:
            update_obj(undertaking.represent.address, address)
            update_obj(undertaking.represent, represent)

    existing_persons = undertaking.contact_persons.all()
    for contact_person in contact_persons:
        # Username already exists flag
        exists = False
        user = (
            User.query
            .filter_by(email=contact_person['email'])
            .first()
        )
        # add or update
        if user:
            update_obj(user, contact_person)
        else:
            user = User(**contact_person)
            # Check if the username is not already in our db
            if not User.query.filter_by(username=contact_person['username']).first():
                db.session.add(user)
            else:
                exists = True
        if user not in existing_persons and not exists:
            undertaking.contact_persons.append(user)

    current_emails = [p.get('email') for p in contact_persons]
    for person in undertaking.contact_persons:
        if person.email not in current_emails:
            undertaking.contact_persons.remove(person)

    undertaking.country_code = undertaking.get_country_code()
    undertaking.country_code_orig = undertaking.get_country_code_orig()
    db.session.add(undertaking)


def eea_double_check(data):
    identifier = """
        Organisation ID: {}
        Organisation status: {}
        Organisation highLevelUses: {}
        Organisation types: {}
    """.format(data['id'], data['status'],
               data['businessProfile']['highLevelUses'], data['types'])
    ok = True

    if not all(('status' in data, data['status'] == 'VALID')):
        message = 'Organisation status differs from VALID.'
        current_app.logger.warning(message + identifier)
        ok = False

    if not all([l.startswith('FGAS_') for l in data['types']]):
        message = "Organisation types elements don't start with 'FGAS_'"
        current_app.logger.warning(message + identifier)
        ok = False

    if not all([l.startswith('fgas.')
                for l in data['businessProfile']['highLevelUses']]):
        message = "Organisation highLevelUses elements don't start with 'fgas.'"
        current_app.logger.warning(message + identifier)
        ok = False

    return ok


def cleanup_unused_users():
    """ Remove users that do not have a company attached """
    unused_users = User.query.filter_by(undertakings=None)

    print "Removing", unused_users.count(), "unused users"
    for u in unused_users:
        db.session.delete(u)
        current_app.logger.info(
            'User {} with email {} has been deleted'.format(
                u.username, u.email))


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
def fgases(days=7, updated_since=None):
    if updated_since:
        try:
            last_update = datetime.strptime(updated_since, '%d/%m/%Y')
        except ValueError:
            return 'Invalid date format. Please use DD/MM/YYYY'
    else:
        days = int(days)
        if days > 0:
            last_update = datetime.now() - timedelta(days=days)
        else:
            last = (
                Undertaking.query
                .order_by(desc(Undertaking.date_updated))
                .first()
            )
            last_update = last.date_updated - timedelta(
                days=1) if last else None

    print "Using last_update {}".format(last_update)
    undertakings = get_latest_undertakings(updated_since=last_update)

    undertakings_count = len([parse_undertaking(u)
                              for u in undertakings
                              if eea_double_check(u)])
    cleanup_unused_users()
    if isinstance(last_update, datetime):
        last_update = last_update.date()
    log = OrganizationLog(
        organizations=undertakings_count,
        using_last_update=last_update)
    db.session.add(log)
    print undertakings_count, "values"

    db.session.commit()
