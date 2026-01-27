import click

from instance.settings import FGAS

from cache_registry.sync import sync_manager
from cache_registry.sync.undertakings import get_latest_undertakings
from cache_registry.sync.utils import get_last_update


def print_all_undertakings(undertakings):
    """
    only used for FGAS as ODS has EU_TYPE countries only
    """
    undertakings_count = 0
    for undertaking in undertakings:
        if undertaking["euLegalRepresentativeCompany"] is None:
            undertaking_address = undertaking.get("address", None)
            if undertaking_address is not None:
                undertaking_country = undertaking_address.get("country", None)
                if undertaking_country is not None:
                    undertaking_country_type = undertaking_country.get("type", None)
                    if undertaking_country_type == "NONEU_TYPE":
                        undertakings_count += 1
                        print(undertaking)

    print(undertakings_count, "values")


@sync_manager.command("fgases_debug_noneu")
@click.option("-u", "--updated", "updated_since", help="Date in DD/MM/YYYY format")
@click.option("-p", "--page_size", "page_size", help="Page size")
def fgases_debug_noneu(days=7, updated_since=None, page_size=None):
    return call_fgases_debug_noneu(days, updated_since, page_size)


def call_fgases_debug_noneu(days=3, updated_since=None, page_size=None):
    # returns a list with all NON EU companies without a legal representative
    last_update = get_last_update(days, updated_since, domain=FGAS)
    undertakings = get_latest_undertakings(
        type_url="/latest/fgasundertakings/",
        updated_since=last_update,
        page_size=page_size,
        domain=FGAS,
    )
    print_all_undertakings(undertakings)
    return True
