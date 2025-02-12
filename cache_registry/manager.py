import click
import collections
import csv
import json
import pprint

from flask import current_app
from flask.cli import AppGroup


from cache_registry.models import (
    Country,
    ProcessAgentUse,
    Undertaking,
    User,
    db,
    loaddata,
)
from cache_registry.sync.bdr import call_bdr
from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods


utils_manager = AppGroup("utils")


@utils_manager.command("check_integrity")
def check_integrity():
    emails = User.query.with_entities(User.email).all()
    duplicates = [e for e, nr in collections.Counter(emails).items() if nr > 1]
    d = {
        e: [
            uid
            for (uid,) in (User.query.filter_by(email=e).with_entities(User.id).all())
        ]
        for (e,) in duplicates
    }

    pprint.pprint(d)


@utils_manager.command("check_passed")
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
            contact_persons.append(
                {
                    "userName": contact_person.username,
                    "firstName": contact_person.first_name,
                    "lastName": contact_person.last_name,
                    "emailAddress": contact_person.email,
                }
            )
        eori = None
        if undertaking.oldcompany:
            eori = undertaking.oldcompany.eori
        data = {
            "id": undertaking.id,
            "name": undertaking.name,
            "phone": undertaking.phone,
            "dateCreated": undertaking.date_created,
            "dateUpdated": undertaking.date_updated,
            "status": undertaking.status,
            "businessProfile": {"highLevelUses": highleveluses},
            "types": types,
            "contactPersons": contact_persons,
            "address": {
                "country": {
                    "code": undertaking.address.country.code,
                    "name": undertaking.address.country.name,
                    "type": undertaking.address.country.type,
                }
            },
            "euLegalRepresentativeCompany": undertaking.represent,
            "domain": undertaking.domain,
            "@type": undertaking.undertaking_type,
            "eoriNumber": eori,
        }
        check_passed = undertaking.check_passed
        if undertaking.domain == "FGAS":
            undertaking.check_passed = eea_double_check_fgases(data)
        elif undertaking.domain == "ODS":
            undertaking.check_passed = eea_double_check_ods(data)
        db.session.commit()
        if not check_passed and undertaking.check_passed:
            call_bdr(undertaking, undertaking.oldcompany_account)


@utils_manager.command("set_ni_previous_reporting_folder")
def set_ni_previous_reporting_folder():
    country = Country.query.filter_by(code="UK")[0]
    undertakings = Undertaking.query.filter_by(country_code="UK_NI")
    for undertaking in undertakings:
        undertaking.country_history.append(country)
        db.session.add(undertaking)
        db.session.commit()


@utils_manager.command("set_users_ecas_id")
def set_users_ecas_id():
    users = User.query.filter_by(ecas_id=None)
    print(f"Users without ecas_id: {users.count()}")
    for user in users:
        if "@" not in user.username:
            print(f"Setting ecas_id for user {user.username}")
            user.ecas_id = user.username
            db.session.add(user)
            db.session.commit()


@utils_manager.command("call_bdr_ni")
def call_bdr_ni():
    undertakings = Undertaking.query.filter_by(country_code="UK_NI")
    for undertaking in undertakings:
        call_bdr(undertaking)


@utils_manager.command("call_bdr_fgas_uk")
def call_bdr_fgas_uk():
    undertakings = Undertaking.query.filter(
        Undertaking.country_code_orig.in_(("UK_GB", "UK"))
    ).filter_by(domain="FGAS")
    for undertaking in undertakings:
        oldcompany_call = False
        if undertaking.oldcompany_account:
            oldcompany_call = True
        call_bdr(undertaking, oldcompany_call)


@utils_manager.command("set_previous_reporting_folder_uk")
def set_previous_reporting_folder_uk():
    country = Country.query.filter_by(code="UK")[0]
    undertakings = Undertaking.query.filter_by(country_code="UK_GB", domain="FGAS")
    for undertaking in undertakings:
        if undertaking.represent and country not in undertaking.country_history:
            undertaking.country_history.append(country)
            db.session.add(undertaking)
            db.session.commit()


@utils_manager.command("import_pau")
@click.option("-f", "--file", "file", help="file_path")
def import_pau(file=None):
    with open(file) as f:
        count = 0
        for row in csv.reader(f, delimiter=","):
            if count == 0:
                count = 1
                continue
            undertaking = Undertaking.query.filter_by(external_id=row[0]).first()
            if not undertaking:
                current_app.logger.warning(f"{row[0]} company does not exists")
                continue
            process_agent_use = ProcessAgentUse(
                type=row[1],
                substance=row[3],
                member_state=row[2],
                pau_use=row[4],
                value=row[5],
                process_name=row[6],
                year=row[7],
                undertaking_id=undertaking.id,
                undertaking=undertaking,
            )
            db.session.add(process_agent_use)
            db.session.commit()


@utils_manager.command("transform_excel_to_json")
@click.option("-f", "--file", "file", help="file_path")
def transform_excel_to_json(file=None):
    json_data = []
    with open(file) as f:
        reader = csv.DictReader(f)
        fieldnames = [
            "type",
            "substance_name_form",
            "is_virgin",
            "company_name",
            "code",
            "result",
            "year",
        ]
        for row in reader:
            json_object = {}
            for field in fieldnames:
                json_object[field] = row[field]
            json_data.append(json_object)
    with open("export_json_stocks.json", "w") as f:
        f.write(json.dumps(json_data))


@utils_manager.command("load_data")
@click.option("-f", "--file", "file", help="file_path")
def load_data(file=None):
    loaddata(file)
