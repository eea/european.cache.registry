import json

from .factories import UndertakingFactory
from fcs import models
from fcs.sync.undertakings import update_undertaking, remove_undertaking


def test_parse_undertaking_new_cp(client):
    with open('testsuite/fixtures/companies.json') as f:
        data = json.load(f)
    username0 = data[0]['contactPersons'][0]['userName']
    username1 = data[1]['contactPersons'][1]['userName']
    update_undertaking(data[0])
    update_undertaking(data[1])
    undertakings = models.Undertaking.query.fgases().all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0
    assert cp[1].username == username1


def test_parse_undertaking_remove_cp(client):
    with open('testsuite/fixtures/companies.json') as f:
        data = json.load(f)
    remaining_username = data[0]['contactPersons'][0]['userName']
    removed_username = data[1]['contactPersons'][1]['userName']
    update_undertaking(data[1])
    update_undertaking(data[0])
    undertakings = models.Undertaking.query.fgases().all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 1
    assert cp[0].username == remaining_username


def test_parse_undertaking_update_cpinfo(client):
    with open('testsuite/fixtures/companies.json') as f:
        data = json.load(f)
    username0 = data[2]['contactPersons'][0]
    username1 = data[2]['contactPersons'][1]
    update_undertaking(data[1])
    update_undertaking(data[2])
    undertakings = models.Undertaking.query.fgases().all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0['username']
    assert cp[0].email == username0['email']
    assert cp[1].username == username1['username']
    assert cp[1].email == username1['email']


def test_remove_undertaking(client):
    with open('testsuite/fixtures/companies.json') as f:
        data = json.load(f)
    UndertakingFactory(external_id=data[0]['id'])
    remove_undertaking(data[0])
    assert models.Undertaking.query.count() == 0
