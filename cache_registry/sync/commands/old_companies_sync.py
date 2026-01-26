import click

from datetime import datetime

from cache_registry.models import Undertaking
from cache_registry.sync import sync_manager
from cache_registry.sync.commands.fgases import call_fgases


@sync_manager.command("old_companies_sync")
@click.option("-u", "--updated", "updated_since", help="Date in dd-MM-YYYY format")
def old_companies_sync(updated_since=None):
    updated = datetime.strptime("01-01-2018", "%d-%m-%Y")
    undertakings = Undertaking.query.filter(
        Undertaking.date_updated <= updated, Undertaking.domain == "FGAS"
    )
    for undertaking in undertakings:
        call_fgases(id=undertaking.external_id)
