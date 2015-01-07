# coding=utf-8
from flask import url_for

from . import factories
from fcs import models


def test_undertaking_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
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
    assert data['name'] == undertaking.name


def test_undertaking_list_vat(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list-by-vat', vat=undertaking.vat))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_undertaking_details(client):
    undertaking = factories.UndertakingFactory()
    oldcompany = factories.OldCompanyFactory(id=2)
    link = factories.OldCompanyLinkFactory()
    link.oldcompany = oldcompany
    link.undertaking = undertaking
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
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


def test_undertaking_details_without_address(client):
    undertaking = factories.UndertakingFactory()
    undertaking.address = None
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
    assert data['address'] is None


def test_undertaking_details_without_representative(client):
    undertaking = factories.UndertakingFactory()
    undertaking.represent = None
    resp = client.get(url_for('api.company-detail', pk=undertaking.external_id))
    data = resp.json
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
    assert data['name'] == undertaking.name


def test_user_companies_by_email(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for('api.user-companies', pk=user.email))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_oldcompany_detail(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for('api.user-companies', pk=user.email))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_candidates_list(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=False)
    oldcompany = factories.OldCompanyFactory(id=2)
    link = factories.OldCompanyLinkFactory()
    link.oldcompany = oldcompany
    link.undertaking = undertaking
    resp = client.get(url_for('api.candidate-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['undertaking']['name'] == undertaking.name
    assert len(data['links']) == 1
    assert data['links'][0]['name'] == oldcompany.name


def test_noncandidates_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.noncandidate-list'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_oldcompany_list_by_status(client):
    undertaking1 = factories.OldCompanyFactory(id=1, valid=True)
    undertaking2 = factories.OldCompanyFactory(id=2, valid=False)
    resp = client.get(url_for('api.oldcompany-list-valid'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking1.name


