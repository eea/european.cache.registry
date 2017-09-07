import requests

from datetime import datetime, timedelta

from fcs.sync.parsers import parse_company
from flask import current_app
from sqlalchemy import desc
from fcs.models import Undertaking, db, OrganizationLog

from . import sync_manager
from .auth import cleanup_unused_users, InvalidResponse, Unauthorized
from .bdr import get_bdr_collections, update_bdr_col_name, get_absolute_url
from .undertakings import update_undertaking, get_latest_undertakings

from .fgases import eea_double_check_fgases
from .ods import eea_double_check_ods


def get_old_companies(obligation):
    auth = current_app.config.get('BDR_API_KEY', '')
    url = get_absolute_url('BDR_API_URL',
                           '/company/obligation/{0}/'.format(obligation))
    params = {'apikey': auth}
    ssl_verify = current_app.config['HTTPS_VERIFY']

    response = requests.get(url, params=params, verify=ssl_verify)
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
            print 'Invalid date format. Please use DD/MM/YYYY'
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

    print "Using last_update {}".format(last_update)
    return last_update


def update_undertakings(undertakings, check_function):
    # import at this level since an import at module level will break
    # due to a circular import between fcs.match and fcs.sync.fgases
    from fcs.match import verify_none
    undertakings_count = 0
    batch = []
    for undertaking in undertakings:
        if check_function(undertaking):
            batch.append(update_undertaking(undertaking))
            if undertakings_count % 10 == 1:
                db.session.add_all(batch)
                db.session.commit()
                del batch[:]
            undertakings_count += 1
            # automatically approve undertaking
            current_app.logger.info(
                'Automatically approve {}'.format(
                    undertaking['external_id']))
            verify_none(undertaking['external_id'], undertaking['domain'],
                        'SYSTEM')

    db.session.add_all(batch)
    db.session.commit()
    del batch[:]
    return undertakings_count


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
                        print undertaking

    print undertakings_count, "values"


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
def fgases(days=7, updated_since=None):
    last_update = get_last_update(days, updated_since, domain='FGAS')
    undertakings = get_latest_undertakings(
        type_url='/latest/fgasundertakings/',
        updated_since=last_update
    )
    undertakings_count = update_undertakings(undertakings,
                                             eea_double_check_fgases)
    cleanup_unused_users()
    log_changes(last_update, undertakings_count, domain='Fgas')
    print undertakings_count, "values"
    db.session.commit()
    return True


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
def ods(days=7, updated_since=None):
    last_update = get_last_update(days, updated_since, domain='ODS')
    undertakings = get_latest_undertakings(
        type_url='/latest/odsundertakings/',
        updated_since=last_update
    )
    undertakings_count = update_undertakings(undertakings,
                                             eea_double_check_ods)
    cleanup_unused_users()
    log_changes(last_update, undertakings_count, domain='Ods')
    print undertakings_count, "values"
    db.session.commit()
    return True


@sync_manager.command
@sync_manager.option('-u', '--updated', dest='updated_since',
                     help="Date in DD/MM/YYYY format")
def fgases_debug_noneu(days=7, updated_since=None):
    # returns a list with all NON EU companies without a legal representative
    last_update = get_last_update(days, updated_since, domain='FGAS')
    undertakings = get_latest_undertakings(
        type_url='/latest/fgasundertakings/',
        updated_since=last_update
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
                    print 'Duplicate collection for company_id: {0} have {1}'\
                          ' and found {2}'.format(c_id, colls[c_id], collection)
        undertakings = Undertaking.query.fgases()
        for undertaking in undertakings:
            ext_id = str(undertaking.external_id)
            title = undertaking.name
            coll = colls.get(ext_id)
            if coll and coll.get('title') != title:
                if update_bdr_col_name(undertaking):
                    print "Updated collection title for: {0}"\
                          .format(ext_id)
    return True


@sync_manager.command
def bdr():
    obligations = current_app.config.get('INTERESTING_OBLIGATIONS', [])
    for obl in obligations:
        print "Getting obligation: ", obl
        companies = get_old_companies(obl)
        print len([parse_company(c, obl) for c in companies]), "values"
    db.session.commit()
    return True
