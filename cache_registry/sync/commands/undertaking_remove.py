import click

from flask import current_app

from cache_registry.models import db, Undertaking
from cache_registry.sync import sync_manager


@sync_manager.command("undertaking_remove")
@click.option("-i", "--external_id", "external_id", help="External id of a company")
@click.option("-d", "--domain", "domain", help="Domain")
def undertaking_remove(external_id, domain):
    undertaking = Undertaking.query.filter_by(
        external_id=external_id, domain=domain
    ).first()
    if undertaking:
        msg = (
            f"Removing undertaking name: {undertaking.name}"
            " with id: {undertaking.id}"
        )
        undertaking.represent_history.clear()
        undertaking.types.clear()
        undertaking.businessprofiles.clear()
        db.session.commit()
        db.session.delete(undertaking)
        db.session.commit()
    else:
        msg = f"No company with id: {external_id} found in the db"
        current_app.logger.warning(msg)
