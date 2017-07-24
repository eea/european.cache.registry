import ast

from flask import current_app

from fcs.models import (
    Undertaking, db, Address, BusinessProfile, User,
    EuLegalRepresentativeCompany
)
from fcs.sync import parsers
from fcs.sync import undertakings as undertakings_module
from fcs.sync.bdr import bdr_request
from fcs.sync.auth import patch_users


def update_obj(obj, d):
    if not d:
        obj = None
    else:
        for name, value in d.iteritems():
            setattr(obj, name, value)
    return obj


def update_bdr_col_name(undertaking):
    """ Update the BDR collection name with the new name
        For the moment, use the API script in the BDR's api/
        folder in order to change the name. This should be changed
        in the future to use a unified API for registries
    """
    DOMAIN_TO_ZOPE_FOLDER = {
        'FGAS': 'fgases'
    }
    endpoint = current_app.config['BDR_ENDPOINT_URL']
    if not endpoint:
        current_app.logger.warning('No bdr endpoint. No bdr call.')
        return True

    params = {
        'country_code': undertaking.country_code.lower(),
        'obligation_folder_name': DOMAIN_TO_ZOPE_FOLDER.get(undertaking.domain),
        'account_uid': str(undertaking.external_id),
        'organisation_name': undertaking.name,
        'oldcompany_account': undertaking.oldcompany_account
    }

    url = endpoint + '/api/update_organisation_name'
    response = bdr_request(url, params)
    error_message = ''
    if response is not None:
        try:
            res = ast.literal_eval(response.content)
        except:
            res = {}
        if not res.get('updated') is True:
            error_message = 'Collection for id: {0} not updated'\
                            .format(undertaking.external_id)
        elif response.status_code != 200:
            error_message = 'Invalid status code: ' + response.status_code
    else:
        error_message = 'Invalid response: ' + str(response)

    if error_message:
        current_app.logger.warning(error_message)
        print error_message
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return not error_message


def parse_undertaking(data):
    data = undertakings_module.patch_undertaking(data['id'], data)
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


def eea_double_check_fgases(data):
    identifier = """
        Organisation ID: {}
        Organisation status: {}
        Organisation highLevelUses: {}
        Organisation types: {}
        Organisation contact persons: {}
        Organisation domain: {}
    """.format(data['id'], data['status'],
               data['businessProfile']['highLevelUses'], data['types'],
               data['contactPersons'], data['domain'])
    ok = True

    manufacturer = 'FGAS_MANUFACTURER_OF_EQUIPMENT_HFCS' in data['types']
    if all([manufacturer, len(data['types']) == 1,
            data['address']['country']['type'] == 'NONEU_TYPE']):
        message = 'NONEU_TYPE Equipment manufacturers only, have no reporting'\
                  ' obligations'
        current_app.logger.warning(message + identifier)
        undertakings_module.remove_undertaking(data)
        ok = False

    if not all(('status' in data, data['status'] in ['VALID', 'DISABLED'])):
        message = 'Organisation status differs from VALID or DISABLED.'
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

    if all([data['status'] == 'DISABLED', len(data['contactPersons']) > 0]):
        message = "Contact Persons available for DISABLED company"
        current_app.logger.warning(message + identifier)
        ok = False

    if not data['domain'] == 'FGAS':
        message = "Organisation domain is not FGAS"
        current_app.logger.warning(message + identifier)
        ok = False

    return ok
