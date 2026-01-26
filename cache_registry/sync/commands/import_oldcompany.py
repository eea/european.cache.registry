import click

from cache_registry.models import (
    db,
    Undertaking,
)
from cache_registry.sync import sync_manager


@sync_manager.command("import_oldcompany")
@click.option("-f", "--file", "file", help="Json file with oldcompany accounts")
def import_oldcompany(file):
    import csv

    with open(file, newline="") as csvfile:
        spamreader = csv.reader(csvfile, delimiter=",", quotechar="|")
        for row in spamreader:
            undertaking = Undertaking.query.filter_by(external_id=row[1]).first()
            if undertaking:
                undertaking.oldcompany_account = row[0]
                db.session.add(undertaking)
                db.session.commit()
