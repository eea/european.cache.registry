import json

from fcs.sync.fgases import parse_undertaking
from fcs import models


def test_parse_undertaking_new_cp(client):
    with open('testsuite/companies.json') as f:
        data = json.load(f)
    username0 = data[0]['contactPersons'][0]['userName']
    username1 = data[1]['contactPersons'][1]['userName']
    parse_undertaking(data[0])
    parse_undertaking(data[1])
    undertakings = models.Undertaking.query.all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0
    assert cp[1].username == username1


def test_parse_undertaking_remove_cp(client):
    with open('testsuite/companies.json') as f:
        data = json.load(f)
    remaining_username = data[0]['contactPersons'][0]['userName']
    parse_undertaking(data[1])
    parse_undertaking(data[0])
    undertakings = models.Undertaking.query.all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 1
    assert cp[0].username == remaining_username


def test_parse_undertaking_update_cpinfo(client):
    with open('testsuite/companies.json') as f:
        data = json.load(f)
    username0 = data[2]['contactPersons'][0]
    username1 = data[2]['contactPersons'][1]
    parse_undertaking(data[1])
    parse_undertaking(data[2])
    undertakings = models.Undertaking.query.all()
    assert len(undertakings) == 1
    u = undertakings[0]
    cp = u.contact_persons
    assert len(cp) == 2
    assert cp[0].username == username0['username']
    assert cp[0].email == username0['email']
    assert cp[1].username == username1['username']
    assert cp[1].email == username1['email']
