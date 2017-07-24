import requests

from flask import current_app

from fcs.models import (
    Undertaking, Address, BusinessProfile,
    EuLegalRepresentativeCompany, User)
from fcs.models import db
from fcs.sync import parsers
from .bdr import update_bdr_col_name, get_absolute_url
from .auth import get_auth, Unauthorized, InvalidResponse, patch_users


def get_latest_undertakings(type_url, updated_since=None):
    """ Get latest undertakings from specific API url """
    auth = get_auth('API_USER', 'API_PASSWORD')
    url = get_absolute_url('API_URL', type_url)
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


def update_obj(obj, d):
    if not d:
        obj = None
    else:
        for name, value in d.iteritems():
            setattr(obj, name, value)
    return obj


def patch_undertaking(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get('PATCH_COMPANIES', {})
    if external_id in patch:
        print("Patching undertaking: {}".format(external_id))
        data.update(patch[external_id])
    return data


def update_undertaking(data):
    """ Create or update undertaking from received data """
    data = patch_undertaking(data['id'], data)
    address = parsers.parse_address(data.pop('address'))
    business_profile = parsers.parse_bp(data.pop('businessProfile'))
    contact_persons = parsers.parse_cp_list(data.pop('contactPersons'))
    represent = parsers.parse_rc(data.pop('euLegalRepresentativeCompany'))

    contact_persons = patch_users(data['id'], contact_persons)
    data['types'] = ','.join(data['types'])
    data['external_id'] = data.pop('id')
    data['date_created'] = parsers.parse_date(data.pop('dateCreated'))
    data['date_updated'] = parsers.parse_date(data.pop('dateUpdated'))
    data['undertaking_type'] = data.pop('@type', None)

    undertaking = (
        Undertaking.query
        .filter_by(external_id=data['external_id'])
        .first()
    )

    if not undertaking:
        undertaking = Undertaking(**data)
    else:
        u_name = undertaking.name
        update_obj(undertaking, data)
        if undertaking.name != u_name:
            if update_bdr_col_name(undertaking):
                print "Updated collection title for: {0}"\
                      .format(undertaking.external_id)

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

    unique_emails = set([cp.get('email') for cp in contact_persons])
    existing_persons = undertaking.contact_persons
    for contact_person in contact_persons:
        user = None
        username = contact_person['username']
        # Check if we have a user with that username
        by_username = User.query.filter_by(username=username).first()
        if not by_username:
            email = contact_person['email']
            # Check if we have a user with that email
            by_email = User.query.filter_by(email=email).first()
            # If we have an email as username, check for duplicate emails
            if '@' in username:
                if len(unique_emails) != len(contact_persons):
                    # If we have duplicate emails, don't match any
                    by_email = None

        user = by_username or by_email

        if user:
            do_update = False
            for key, value in contact_person.items():
                if value != getattr(user, key):
                    do_update = True
            if do_update:
                update_obj(user, contact_person)
        else:
            user = User(**contact_person)
            db.session.add(user)
        if user not in existing_persons:
            undertaking.contact_persons.append(user)

    current_emails = [p.get('email') for p in contact_persons]
    current_usernames = [p.get('username') for p in contact_persons]
    for person in undertaking.contact_persons:
        if person.email not in current_emails or \
           person.username not in current_usernames:
            undertaking.contact_persons.remove(person)

    undertaking.country_code = undertaking.get_country_code()
    undertaking.country_code_orig = undertaking.get_country_code_orig()
    return undertaking


def remove_undertaking(data):
    """Remove undertaking."""
    undertaking = (
        Undertaking.query
        .filter_by(external_id=data.get('id'))
        .first()
    )
    if undertaking:
        msg = 'Removing undertaking name: {}'\
              ' with id: {}'.format(undertaking.name, undertaking.id)
        current_app.logger.warning(msg)
        db.session.delete(undertaking)
    else:
        msg = 'No company with id: {} found in the db'.format(data.get('id'))
        current_app.logger.warning(msg)
