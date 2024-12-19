import json

from cache_registry.models import Auditor
from cache_registry.sync.auditors import update_auditor


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
    assert cp[0].username == username0["username"]
    assert cp[0].email == username0["email"]
    assert cp[0].type.value == username0["type"]
    assert cp[1].username == username1["username"]
    assert cp[1].email == username1["email"]
    assert cp[1].type.value == username1["type"]
