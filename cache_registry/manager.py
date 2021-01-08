import collections
import pprint

from flask_script import Manager

from cache_registry.models import Country, db, User, Undertaking
from cache_registry.sync.bdr import call_bdr
from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods


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
        eori = None
        if undertaking.oldcompany:
            eori = undertaking.oldcompany.eori
        data = {
            'id': undertaking.id,
            'name': undertaking.name,
            'phone': undertaking.phone,
            'dateCreated': undertaking.date_created,
            'dateUpdated': undertaking.date_updated,
            'status': undertaking.status,
            'businessProfile': {
                'highLevelUses': highleveluses
            },
            'types': types,
            'contactPersons': contact_persons,
            'address': {
                'country': {
                    'code':undertaking.address.country.code,
                    'name': undertaking.address.country.name,
                    'type': undertaking.address.country.type
                }
            },
            'euLegalRepresentativeCompany': undertaking.represent,
            'domain': undertaking.domain,
            '@type': undertaking.undertaking_type,
            'eoriNumber': eori
        }
        check_passed = undertaking.check_passed
        if undertaking.domain == 'FGAS':
            undertaking.check_passed = eea_double_check_fgases(data)
        elif undertaking.domain == 'ODS':
            undertaking.check_passed = eea_double_check_ods(data)
        db.session.commit()
        if check_passed == False and undertaking.check_passed == True:
            call_bdr(undertaking, undertaking.oldcompany_account)

@utils_manager.command
def set_ni_previous_reporting_folder():
    country = Country.query.filter_by(code='UK')[0]
    undertakings = Undertaking.query.filter_by(country_code='UK_NI')
    for undertaking in undertakings:
        undertaking.country_history.append(country)
        db.session.add(undertaking)
        db.session.commit()
