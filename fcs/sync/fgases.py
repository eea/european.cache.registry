from datetime import datetime, timedelta

import ast
import requests

from sqlalchemy import desc
from flask import current_app
from sqlalchemy.orm import session

from fcs.models import (
    Undertaking, db, Address, Country, BusinessProfile, User,
    EuLegalRepresentativeCompany, OrganizationLog,
)
from fcs.sync import sync_manager, Unauthorized, InvalidResponse
from fcs.sync.bdr import get_auth as get_bdr_auth
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


def bdr_request(url, params=None):
    auth = get_bdr_auth()
    ssl_verify = current_app.config['HTTPS_VERIFY']

    response = None
    try:
        response = requests.get(url, params=params, auth=auth,
                                verify=ssl_verify)
    except requests.ConnectionError:
        error_message = 'BDR was unreachable - {}'.format(datetime.now())
        current_app.logger.warning(error_message)
        print error_message
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return response


def get_bdr_collections():
    endpoint = current_app.config['BDR_ENDPOINT_URL']
    url = endpoint + '/api/collections_json'
    response = bdr_request(url)
    if response and response.status_code == 200:
        return response.json()


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


def eea_double_check(data):
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
        remove_undertaking(data)
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
    # import at this level since an import at module level will break
    # due to a circular import between fcs.match and fcs.sync.fgases
    from fcs.match import verify_none
    with session.no_autoflush:
        if updated_since:
            try:
                last_update = datetime.strptime(updated_since, '%d/%m/%Y')
            except ValueError:
                print 'Invalid date format. Please use DD/MM/YYYY'
                return False
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

        undertakings_count = 0
        batch = []
        for undertaking in undertakings:
            if eea_double_check(undertaking):
                batch.append(parse_undertaking(undertaking))
                if undertakings_count % 10 == 1:
                    db.session.add_all(batch)
                    db.session.commit()
                    del batch[:]
                undertakings_count += 1
                # automatically approve undertaking
                current_app.logger.info(
                    'Automatically approve {}'.format(
                        undertaking['external_id']))
                verify_none(undertaking['external_id'], 'SYSTEM')

        db.session.add_all(batch)
        db.session.commit()
        del batch[:]

        cleanup_unused_users()
        if isinstance(last_update, datetime):
            last_update = last_update.date()
        log = OrganizationLog(
            organizations=undertakings_count,
            using_last_update=last_update)
        db.session.add(log)
        print undertakings_count, "values"
        db.session.commit()
    return True


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
def fgases_debug_noneu(days=7, updated_since=None):
    # returns a list with all NON EU companies without a legal representative
    # import at this level since an import at module level will break
    # due to a circular import between fcs.match and fcs.sync.fgases
    from fcs.match import verify_none

    if updated_since:
        try:
            last_update = datetime.strptime(updated_since, '%d/%m/%Y')
        except ValueError:
            print 'Invalid date format. Please use DD/MM/YYYY'
            return False
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

    undertakings_count = 0
    for undertaking in undertakings:
        if undertaking['euLegalRepresentativeCompany'] == None:
            undertaking_address = undertaking.get('address', None)
            if undertaking_address != None:
                undertaking_country = undertaking_address.get('country', None)
                if undertaking_country != None:
                    undertaking_country_type = undertaking_country.get('type', None)
                    if undertaking_country_type == 'NONEU_TYPE':
                        undertakings_count += 1
                        print undertaking

    print undertakings_count, "values"
    return True


@sync_manager.command
def sync_collections_title():
    collections = get_bdr_collections()
    if collections:
        colls = {}
        for collection in collections:
            c_id = collection.get('company_id')
            if c_id:
                if not colls.get(c_id):
                    colls[c_id] = collection
                else:
                    print 'Duplicate collection for company_id: {0} have {1}'\
                          ' and found {2}'.format(c_id, colls[c_id], collection)
        undertakings = Undertaking.query.all()
        for undertaking in undertakings:
            ext_id = str(undertaking.external_id)
            title = undertaking.name
            coll = colls.get(ext_id)
            if coll and coll.get('title') != title:
                if update_bdr_col_name(undertaking):
                    print "Updated collection title for: {0}"\
                          .format(ext_id)
    return True
