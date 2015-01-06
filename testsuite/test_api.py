# coding=utf-8
from flask import url_for

from . import factories


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


def test_undertaking_list_add(client):
    undertaking = factories.UndertakingFactory()
    undertaking.oldcompany_verified = False
    resp = client.get(url_for('api.company-list-all'))
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

