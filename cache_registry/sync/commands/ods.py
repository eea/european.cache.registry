import click

from instance.settings import ODS

from cache_registry.models import (
    Undertaking,
    db,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.auth import cleanup_unused_users
from cache_registry.sync.bdr import (
    call_bdr,
    check_if_company_folder_exists,
)
from cache_registry.sync.eea_double_checks.ods import eea_double_check_ods
from cache_registry.sync.undertakings import (
    get_latest_undertakings,
    update_undertakings,
)
from cache_registry.sync.utils import get_last_update, log_changes


@sync_manager.command("ods")
@click.option("-d", "--days", "days", help="Number of days the update is done for.")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
@click.option("-i", "--external_id", "id", help="External id of a company")
@click.option(
    "-r", "--registration_id", "registration_id", help="Registration id of a company"
)
def ods(days=7, updated_since=None, page_size=200, id=None, registration_id=None):
    return call_ods(days, updated_since, page_size, id, registration_id)


def call_ods(days=3, updated_since=None, page_size=200, id=None, registration_id=None):
    if not id and not registration_id:
        last_update = get_last_update(days, updated_since, domain=ODS)
    else:
        last_update = None
        identifier = id if id else registration_id
        print(f"Fetching data for company {identifier}")
    undertakings = get_latest_undertakings(
        type_url="/latest/odsundertakings/",
        updated_since=last_update,
        page_size=page_size,
        id=id,
        registration_id=registration_id,
        domain=ODS,
    )
    (undertakings_for_call_bdr, undertakings_count) = update_undertakings(
        undertakings, eea_double_check_ods
    )
    cleanup_unused_users()
    if not id and not registration_id:
        log_changes(last_update, undertakings_count, domain=ODS)
        print(undertakings_count, "values")
    db.session.commit()
    for undertaking in undertakings_for_call_bdr:
        undertaking_obj = Undertaking.query.filter_by(
            external_id=undertaking["external_id"], domain=ODS
        ).first()
        if undertaking_obj.check_passed:
            if not check_if_company_folder_exists(undertaking_obj):
                call_bdr(undertaking_obj, undertaking_obj.oldcompany_account)
    return True
