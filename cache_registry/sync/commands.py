import requests
from os import environ

from flask_script.commands import InvalidCommand
from datetime import datetime, timedelta

from cache_registry.sync.parsers import parse_company
from flask import current_app
from sqlalchemy import desc
from cache_registry.models import Undertaking, db, OrganizationLog, Country, DeliveryLicence
from instance.settings import FGAS, ODS
from . import sync_manager
from .auth import cleanup_unused_users, InvalidResponse, Unauthorized
from .bdr import get_bdr_collections, update_bdr_col_name, get_absolute_url, call_bdr
from .licences import (
    aggregate_licences_to_undertakings,
    aggregate_licence_to_substance,
    delete_all_substances_and_licences,
    get_licences,
    get_or_create_substance,
    get_or_create_delivery,
    parse_licence,
)
from .undertakings import get_latest_undertakings, update_undertaking

from .fgases import eea_double_check_fgases
from .ods import eea_double_check_ods


def get_old_companies(obligation):
    token = current_app.config.get('BDR_API_KEY', '')
    if obligation.lower() == 'fgas':
        obligation = 'fgases'
    url = get_absolute_url('BDR_API_URL',
                           '/company/obligation/{0}/'.format(obligation))
    headers = {'Authorization': token}
    ssl_verify = current_app.config['HTTPS_VERIFY']
    response = requests.get(url, headers=headers, verify=ssl_verify)
    if response.status_code in (401, 403):
        raise Unauthorized()
    if response.status_code != 200:
        raise InvalidResponse()

    return response.json()


def get_last_update(days, updated_since, domain):
    if updated_since:
        try:
            last_update = datetime.strptime(updated_since, '%d/%m/%Y')
        except ValueError:
            print('Invalid date format. Please use DD/MM/YYYY')
            return False
    else:
        days = int(days)
        if days > 0:
            last_update = datetime.now() - timedelta(days=days)
        else:
            last = (
                Undertaking.query.filter_by(domain=domain)
                .order_by(desc(Undertaking.date_updated)).first()
            )
            last_update = last.date_updated - timedelta(
                days=1) if last else None

    print("Using last_update {}".format(last_update))
    return last_update


def update_undertakings(undertakings, check_function):
    # import at this level since an import at module level will break
    # due to a circular import between cache_registry.match and cache_registry.sync.fgases
    from cache_registry.match import verify_none
    undertakings_count = 0
    undertakings_with_changed_represent = []
    for undertaking in undertakings:
        undertaking_exists = Undertaking.query.filter_by(external_id=undertaking['id']).first()
        check_passed_exists = None
        if undertaking_exists:
            check_passed_exists = undertaking_exists.check_passed
        check_passed = check_function(undertaking)
        if (not undertaking['@type'] == 'ODSUndertaking') or check_passed or undertaking_exists:
            (_, represent) = update_undertaking(undertaking, check_passed=check_passed)
            undertakings_count += 1
            if (
                represent and check_passed
                or represent and undertaking_exists and not check_passed
                or check_passed_exists != check_passed and check_passed
            ):
                undertakings_with_changed_represent.append(undertaking)

    return undertakings_with_changed_represent, undertakings_count


def log_changes(last_update, undertakings_count, domain):
    if isinstance(last_update, datetime):
        last_update = last_update.date()
    log = OrganizationLog(
        organizations=undertakings_count,
        using_last_update=last_update,
        domain=domain)
    db.session.add(log)


def print_all_undertakings(undertakings):
    """
    only used for FGAS as ODS has EU_TYPE countries only
    """
    undertakings_count = 0
    for undertaking in undertakings:
        if undertaking['euLegalRepresentativeCompany'] is None:
            undertaking_address = undertaking.get('address', None)
            if undertaking_address is not None:
                undertaking_country = undertaking_address.get('country', None)
                if undertaking_country is not None:
                    undertaking_country_type = undertaking_country.get('type', None)
                    if undertaking_country_type == 'NONEU_TYPE':
                        undertakings_count += 1
                        print(undertaking)

    print(undertakings_count, "values")


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
@sync_manager.option('-p', '--page_size', dest='page_size',
                     help="Page size")
@sync_manager.option('-i', '--external_id', dest='external_id',
                     help="External id of a company")
def fgases(days=7, updated_since=None, page_size=None, id=None):
    if not id:
        last_update = get_last_update(days, updated_since, domain=FGAS)
    else:
        last_update = None
        print("Fetching data for company {}".format(id))

    undertakings = get_latest_undertakings(
        type_url='/latest/fgasundertakings/',
        updated_since=last_update,
        page_size=page_size,
        id=id
    )
    (undertakings_with_changed_repr,undertakings_count) = update_undertakings(undertakings,
                                             eea_double_check_fgases)
    cleanup_unused_users()
    if not id:
        log_changes(last_update, undertakings_count, domain=FGAS)
        print(undertakings_count, "values")
    db.session.commit()
    for undertaking in undertakings_with_changed_repr:
        undertaking_obj = Undertaking.query.filter_by(external_id=undertaking['external_id']).first()
        call_bdr(undertaking_obj, undertaking_obj.oldcompany_account)
    return True


@sync_manager.option('-i', '--external_id', dest='external_id',
                     help="External id of a company")
@sync_manager.option('-d', '--domain', dest='domain',
                     help="Domain")
def undertaking_remove(external_id, domain):
    undertaking = (
        Undertaking.query
        .filter_by(external_id=external_id, domain=domain)
        .first()
    )
    if undertaking:
        msg = 'Removing undertaking name: {}'\
              ' with id: {}'.format(undertaking.name, undertaking.id)
        undertaking.represent_history.clear()
        undertaking.types.clear()
        undertaking.businessprofiles.clear()
        db.session.commit()
        db.session.delete(undertaking)
        db.session.commit()
    else:
        msg = 'No company with id: {} found in the db'.format(external_id)
        current_app.logger.warning(msg)


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
@sync_manager.option('-p', '--page_size', dest='page_size',
                     help="Page size")
@sync_manager.option('-i', '--external_id', dest='external_id',
                     help="External id of a company")
def ods(days=7, updated_since=None, page_size=None, id=None):
    if not id:
        last_update = get_last_update(days, updated_since, domain=ODS)
    else:
        last_update = None
        print("Fetching data for company {}".format(id))

    undertakings = get_latest_undertakings(
        type_url='/latest/odsundertakings/',
        updated_since=last_update,
        page_size=page_size,
        id=id
    )

    (undertakings_with_changed_repr,undertakings_count) = update_undertakings(undertakings,
                                             eea_double_check_ods)
    cleanup_unused_users()
    if not id:
        log_changes(last_update, undertakings_count, domain=ODS)
        print(undertakings_count, "values")
    db.session.commit()
    for undertaking in undertakings_with_changed_repr:
        undertaking_obj = Undertaking.query.filter_by(external_id=undertaking['external_id']).first()
        call_bdr(undertaking_obj, undertaking_obj.oldcompany_account)
    return True


@sync_manager.command
@sync_manager.option('-y', '--year', dest='year',
                     help="Licences from year x")
@sync_manager.option('-p', '--page_size', dest='page_size',
                     help="Page size")

def licences(year, page_size=200):
    data = get_licences(year=year, page_size=page_size)
    companies = aggregate_licences_to_undertakings(data)
    for company, data in companies.items():
        undertaking = Undertaking.query.filter_by(external_id=company, domain='ODS').first()
        delivery_licence = get_or_create_delivery(year, undertaking)
        if delivery_licence.updated_since == None or data['updated_since'] > delivery_licence.updated_since:
            delete_all_substances_and_licences(delivery_licence)
            for licence in data['licences']:
                substance = get_or_create_substance(delivery_licence, licence)
                if not substance:
                    substance_name =  "{} ({})".format(licence['chemicalName'], licence['mixtureNatureType'].lower())
                    message = 'Substance {} could not be translated or Country code {} or Substance country code {} could not be translated.'.format(
                        substance_name, licence['organizationCountryName'], licence['internationalPartyCountryName'])
                    current_app.logger.error(message)
                    continue
                licence_object = parse_licence(licence, undertaking.id, substance)
            aggregate_licence_to_substance(delivery_licence, year)
            delivery_licence.updated_since = data['updated_since']
            db.session.add(delivery_licence)
            db.session.commit()
    return True


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
@sync_manager.option('-p', '--page_size', dest='page_size',
                     help="Page size")
def fgases_debug_noneu(days=7, updated_since=None, page_size=None):
    # returns a list with all NON EU companies without a legal representative
    last_update = get_last_update(days, updated_since, domain=FGAS)
    undertakings = get_latest_undertakings(
        type_url='/latest/fgasundertakings/',
        updated_since=last_update,
        page_size=page_size
    )
    print_all_undertakings(undertakings)
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
                    print('Duplicate collection for company_id: {0} have {1}'\
                          ' and found {2}'.format(c_id, colls[c_id], collection))
        undertakings = Undertaking.query
        for undertaking in undertakings:
            ext_id = str(undertaking.external_id)
            title = undertaking.name
            coll = colls.get(ext_id)
            if coll and coll.get('title') != title:
                if update_bdr_col_name(undertaking):
                    print("Updated collection title for: {0}".format(ext_id))
    return True


@sync_manager.command
def bdr():
    obligations = current_app.config.get('MANUAL_VERIFY_ALL_COMPANIES', [])
    for obl in obligations:
        if obl:
            print("Getting obligation: ", obl)
            companies = get_old_companies(obl.lower())
            print(len([parse_company(c, obl) for c in companies]), "values")
    db.session.commit()
    return True


@sync_manager.command

def remove_all_licences_substances():
    deliveries = DeliveryLicence.query.all()
    for delivery in deliveries:
        delete_all_substances_and_licences(delivery)
        delivery.updated_since = None
        db.session.add(delivery)
        db.session.commit()
    return True
