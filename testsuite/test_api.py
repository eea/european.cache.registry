# coding=utf-8
from flask import url_for

from . import factories


def test_undertaking_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id
    assert data['name'] == undertaking.name
    assert data['website'] == undertaking.website
    assert data['phone'] == undertaking.phone
    assert data['domain'] == undertaking.domain
    assert data['date_created'] == undertaking.date_created.strftime('%d/%m/%Y')
    assert data['date_updated'] == undertaking.date_updated.strftime('%d/%m/%Y')
    assert data['status'] == undertaking.status
    assert data['undertaking_type'] == undertaking.undertaking_type
    assert data['vat'] == undertaking.vat
    assert data['types'] == undertaking.types
    assert data['oldcompany_verified'] == undertaking.oldcompany_verified
    assert data['oldcompany_account'] == undertaking.oldcompany_account
    assert data['oldcompany_extid'] == undertaking.oldcompany_extid


def test_undertaking_list_all(client):
    undertaking = factories.UndertakingFactory()
    undertaking.oldcompany_verified = False
    resp = client.get(url_for('api.company-list-all'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_list_vat(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list-by-vat', vat=undertaking.vat))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_details(client):
    undertaking = factories.UndertakingFactory(oldcompany=None)
    oldcompany = factories.OldCompanyFactory(id=2)
    link = factories.OldCompanyLinkFactory(oldcompany=oldcompany,
                                           undertaking=undertaking)
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['name'] == undertaking.name
    assert data['website'] == undertaking.website
    assert data['phone'] == undertaking.phone
    assert data['domain'] == undertaking.domain
    assert data['status'] == undertaking.status
    assert data['vat'] == undertaking.vat
    assert data['oldcompany_verified'] == undertaking.oldcompany_verified
    assert data['oldcompany_account'] == undertaking.oldcompany_account
    assert data['oldcompany_extid'] == undertaking.oldcompany_extid
    assert data['representative']['name'] == undertaking.represent.name
    assert data['address']['zipcode'] == undertaking.address.zipcode
    assert data['candidates'][0]['company_id'] == oldcompany.external_id


def test_undertaking_details_without_address(client):
    undertaking = factories.UndertakingFactory()
    undertaking.address = None
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['address'] is None


def test_undertaking_details_without_representative(client):
    undertaking = factories.UndertakingFactory()
    undertaking.represent = None
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['representative'] is None


def test_user_list(client):
    user = factories.UserFactory()
    resp = client.get(url_for('api.user-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['username'] == user.username


def test_user_companies_by_username(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for('api.user-companies', pk=user.username))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id


def test_user_companies_by_email(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for('api.user-companies', pk=user.email))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id


def test_candidates_list(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=False)
    oldcompany = factories.OldCompanyFactory(id=2)
    link = factories.OldCompanyLinkFactory(oldcompany=oldcompany,
                                           undertaking=undertaking)
    resp = client.get(url_for('api.candidate-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['undertaking']['company_id'] == undertaking.external_id
    assert len(data['links']) == 1
    assert data['links'][0]['company_id'] == oldcompany.external_id


def test_noncandidates_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.noncandidate-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_oldcompany_list_valid(client):
    undertaking1 = factories.OldCompanyFactory(id=1, valid=True)
    undertaking2 = factories.OldCompanyFactory(id=2, valid=False)
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


def test_unverify_link(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=False)
    link = factories.OldCompanyLinkFactory(oldcompany=undertaking.oldcompany,
                                           undertaking=undertaking)
    resp = client.post(url_for('api.candidate-unverify',
                               undertaking_id=undertaking.external_id),
                       dict(user='test_user'))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
