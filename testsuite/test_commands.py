import json

from fcs import models
from fcs.sync.commands import update_undertakings
from fcs.sync.fgases import eea_double_check_fgases
from fcs.sync.ods import eea_double_check_ods


def test_update_undertakings_fgas(client):
    with open('testsuite/fixtures/companies-fgas.json') as file:
        data = json.load(file)
    undertakings_count = update_undertakings(data, eea_double_check_fgases)
    assert undertakings_count == len(data)
    assert models.Undertaking.query.fgases().count() == len(data)


def test_update_undertakings_ods(client):
    with open('testsuite/fixtures/companies-ods.json') as file:
        data = json.load(file)
        for undertaking in data:
            ok = eea_double_check_ods(undertaking)
            assert ok
