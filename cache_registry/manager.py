import collections
import pprint

from flask.ext.script import Manager

from cache_registry.models import db, User, Undertaking
from cache_registry.sync.fgases import eea_double_check_fgases


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


@utils_manager.command
def check_passed():
    undertakings = Undertaking.query.all()
    for undertaking in undertakings:
        highleveluses = []
        for businessprofile in undertaking.businessprofiles:
            highleveluses.append(businessprofile.highleveluses)
        types = []
        for type in undertaking.types:
            types.append(type.type)
        contact_persons = []
        for contact_person in undertaking.contact_persons:
            contact_persons.append({
                "userName": contact_person.username,
                "firstName": contact_person.first_name,
                "lastName": contact_person.last_name,
                "emailAddress": contact_person.email
            })
        data = {
            'id': undertaking.id,
            'status': undertaking.status,
            'businessProfile': {
                'highLevelUses': highleveluses
            },
            'types': types,
            'contactPersons': contact_persons,
            'address': {
                'country': {
                    'type': undertaking.address.country.type
                }
            },
            'euLegalRepresentativeCompany': undertaking.represent,
            'domain': undertaking.domain
        }
        undertaking.check_passed = eea_double_check_fgases(data)
        db.session.commit()
