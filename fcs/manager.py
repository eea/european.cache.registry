import collections
import pprint

from flask_script import Manager

from fcs.models import User


utils_manager = Manager()


@utils_manager.command
def check_integrity():
    emails = User.query.with_entities(User.email).all()
    duplicates = [e for e, nr in collections.Counter(emails).items() if nr > 1]
    d = {e: [uid for (uid, ) in (User.query
                                 .filter_by(email=e)
                                 .with_entities(User.id)
                                 .all())]
         for (e, ) in duplicates}

    pprint.pprint(d)
