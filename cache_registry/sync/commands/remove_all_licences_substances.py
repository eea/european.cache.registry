import click

from cache_registry.models import (
    db,
    DeliveryLicence,
)
from cache_registry.sync import sync_manager
from cache_registry.sync.licences_aggregation import delete_all_substances_and_licences


@sync_manager.command("remove_all_licences_substances")
@click.option("-y", "--year", "year")
def remove_all_licences_substances(year=None):
    if year:
        deliveries = DeliveryLicence.query.filter_by(year=year)
    else:
        deliveries = DeliveryLicence.query.all()
    for delivery in deliveries:
        delete_all_substances_and_licences(delivery)
        delivery.updated_since = None
        db.session.add(delivery)
        db.session.commit()
    return True
