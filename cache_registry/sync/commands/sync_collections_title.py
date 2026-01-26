from cache_registry.models import Undertaking
from cache_registry.sync import sync_manager
from cache_registry.sync.bdr import (
    get_bdr_collections,
    update_bdr_col_name,
)


@sync_manager.command("sync_collections_title")
def sync_collections_title():
    return call_sync_collections_title()


def call_sync_collections_title():
    collections = get_bdr_collections()
    if collections:
        colls = {}
        for collection in collections:
            c_id = collection.get("company_id")
            if c_id:
                if not colls.get(c_id):
                    colls[c_id] = collection
                else:
                    print(
                        f"Duplicate collection for company_id: {c_id} have {colls[c_id]} \
                        and found {collection}"
                    )
        undertakings = Undertaking.query
        for undertaking in undertakings:
            ext_id = str(undertaking.external_id)
            title = undertaking.name
            coll = colls.get(ext_id)
            if coll and coll.get("title") != title:
                if update_bdr_col_name(undertaking):
                    print(f"Updated collection title for: {ext_id}")
    return True
