import json

from cache_registry.models import Auditor
from cache_registry.sync.auditors import update_auditor


def test_parse_auditor(client):
    with open("testsuite/fixtures/auditors.json") as f:
        data = json.load(f)
    update_auditor(data[0])
    auditors = Auditor.query.all()

    assert len(auditors) == 1
    auditor = auditors[0]
    assert auditor.name == data[0]["name"]
    assert auditor.auditor_uid == data[0]["auditorUID"]
    assert auditor.status.value == data[0]["status"]
    assert auditor.date_created.strftime("%d/%m/%Y") == data[0]["dateCreated"]
    assert auditor.date_updated.strftime("%d/%m/%Y") == data[0]["dateUpdated"]
    assert auditor.ets_accreditation == data[0]["etsAccreditation"]["enabled"]
    assert auditor.ms_accreditation == data[0]["msAccreditation"]["enabled"]
    assert auditor.address.street == data[0]["address"]["street"]
    assert auditor.address.number == data[0]["address"]["number"]
    assert auditor.address.city == data[0]["address"]["city"]
    assert auditor.address.zipcode == data[0]["address"]["zipCode"]
    assert auditor.phone == data[0]["phone"]
    assert auditor.website == data[0]["website"]
    assert len(auditor.contact_persons) == len(data[0]["contactPersons"])
    assert (
        auditor.contact_persons[0].username == data[0]["contactPersons"][0]["userName"]
    )
    assert (
        auditor.contact_persons[0].email == data[0]["contactPersons"][0]["emailAddress"]
    )
    assert auditor.contact_persons[0].type.value == data[0]["contactPersons"][0]["type"]


def test_parse_auditor_new_cp(client):
    with open("testsuite/fixtures/auditors.json") as f:
        data = json.load(f)

    username0 = data[0]["contactPersons"][0]["userName"]
    username1 = data[1]["contactPersons"][1]["userName"]
    update_auditor(data[0])
    update_auditor(data[1])

    auditors = Auditor.query.all()
    assert len(auditors) == 1

    cp = auditors[0].contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0
    assert cp[1].username == username1


def test_parse_auditor_remove_cp(client):
    with open("testsuite/fixtures/auditors.json") as f:
        data = json.load(f)

    remaining_username = data[0]["contactPersons"][0]["userName"]
    update_auditor(data[1])
    update_auditor(data[0])

    auditors = Auditor.query.all()
    assert len(auditors) == 1

    cp = auditors[0].contact_persons
    assert len(cp) == 1
    assert cp[0].username == remaining_username


def test_parse_auditor_update_cpinfo(client):
    with open("testsuite/fixtures/auditors.json") as f:
        data = json.load(f)

    username0 = data[2]["contactPersons"][0]
    username1 = data[2]["contactPersons"][1]
    update_auditor(data[1])
    update_auditor(data[2])

    auditors = Auditor.query.all()
    assert len(auditors) == 1

    cp = auditors[0].contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0["userName"]
    assert cp[0].email == username0["emailAddress"]
    assert cp[0].type.value == username0["type"]
    assert cp[1].username == username1["userName"]
    assert cp[1].email == username1["emailAddress"]
    assert cp[1].type.value == username1["type"]
