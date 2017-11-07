from flask import url_for
from testsuite import factories


def test_oldcompany_list_valid(client):
    undertaking1 = factories.OldCompanyFactory(valid=True)
    undertaking2 = factories.OldCompanyFactory(valid=False)
    resp = client.get(url_for('api.oldcompany-list-valid'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking1.external_id


def test_oldcompany_list_invalid(client):
    undertaking1 = factories.OldCompanyFactory(id=1, valid=True)
    undertaking2 = factories.OldCompanyFactory(id=2, valid=False)
    resp = client.get(url_for('api.oldcompany-list-invalid'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking2.external_id


def test_oldcompany_set_valid(client):
    oldcompany = factories.OldCompanyFactory(valid=False)
    resp = client.post(url_for('api.oldcompany-set-valid',
                               pk=oldcompany.external_id))
    data = resp.body
    assert data == 'true'
    assert oldcompany.valid is True


def test_oldcompany_set_invalid(client):
    oldcompany = factories.OldCompanyFactory(valid=True)
    resp = client.post(url_for('api.oldcompany-set-invalid',
                               pk=oldcompany.external_id))
    data = resp.body
    assert data == 'true'
    assert oldcompany.valid is False
