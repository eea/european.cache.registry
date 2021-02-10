import collections
import json
import pprint

from flask_script import Manager
from flask import current_app

from cache_registry.models import Country, db, User, Undertaking, ProcessAgentUse
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

@utils_manager.command
def call_bdr_ni():
    country = Country.query.filter_by(code='UK')[0]
    undertakings = Undertaking.query.filter_by(country_code='UK_NI')
    for undertaking in undertakings:
        call_bdr(undertaking)

@utils_manager.command
def call_bdr_fgas_uk():
    country = Country.query.filter_by(code='UK')[0]
    undertakings = Undertaking.query.filter_by(country_code='UK_GB', domain='FGAS')
    for undertaking in undertakings:
        call_bdr(undertaking)

@utils_manager.command
def set_previous_reporting_folder_uk():
    country = Country.query.filter_by(code='UK')[0]
    undertakings = Undertaking.query.filter_by(country_code='UK_GB', domain='FGAS')
    for undertaking in undertakings:
        if undertaking.represent and country not in undertaking.country_history:
            undertaking.country_history.append(country)
            db.session.add(undertaking)
            db.session.commit()

@utils_manager.command
@utils_manager.option('-f', '--file', dest='file',
                     help="file_path")
def import_pau(file=None):
    import csv

    with open(file) as f:
        count = 0
        for row in csv.reader(f, delimiter=','):
            if count == 0:
                count = 1
                continue
            undertaking = Undertaking.query.filter_by(external_id=row[0]).first()
            if not undertaking:
                current_app.logger.warning("{} company does not exists".format(row[0]))
                continue
            process_agent_use = ProcessAgentUse(
                type = row[1],
                substance = row[4],
                member_state = row[3],
                pau_use = row[5],
                value = row[6],
                process_name = row[7],
                year = row[8],
                undertaking_id = undertaking.id,
                undertaking = undertaking,
            )
            db.session.add(process_agent_use)
            db.session.commit()
