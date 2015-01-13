# coding=utf-8
import requests

from flask import url_for
from . import factories

from fcs.match import run


def mockreturn(url, **kwargs):
    res = requests.Response()
    res.status_code = 200
    res.headers['content_type'] = 'application/json'
    res.contents = '{"message": "mess", "status": "success"}'
    return res


def test_verify_link(client, monkeypatch):
    monkeypatch.setattr(requests, 'get', mockreturn)
    undertaking = factories.UndertakingFactory(oldcompany=None)
    oldcompany = factories.OldCompanyFactory(id=2)
    factories.OldCompanyLinkFactory(oldcompany=oldcompany,
                                    undertaking=undertaking)
    client.post(url_for('api.candidate-verify',
                        undertaking_id=undertaking.external_id,
                        oldcompany_id=oldcompany.external_id),
                dict(user='test_user'))
    resp = client.get(url_for('api.matching-log'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['verified'] is True
    assert data['company_id'] == undertaking.external_id
    assert data['oldcompany_id'] == oldcompany.external_id
    assert data['user'] == 'test_user'
    assert data['oldcompany_account'] == oldcompany.account


def test_verify_none(client, monkeypatch):
    monkeypatch.setattr(requests, 'get', mockreturn)
    undertaking = factories.UndertakingFactory(oldcompany=None)
    oldcompany = factories.OldCompanyFactory(id=2)
    factories.OldCompanyLinkFactory(undertaking=undertaking,
                                    oldcompany=oldcompany)

    client.post(url_for('api.candidate-verify-none',
                        undertaking_id=undertaking.external_id),
                dict(user='test_user'))

    resp = client.get(url_for('api.matching-log'))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['verified'] is True
    assert data['user'] == 'test_user'
    assert data['oldcompany_id'] is None
    assert data['company_id'] == 10


def test_auto_verify_companies(client, monkeypatch):
    monkeypatch.setattr(requests, 'get', mockreturn)
    undertaking = factories.UndertakingFactory(oldcompany=None,
                                               oldcompany_verified=False)
    oldcompany = factories.OldCompanyFactory(id=2)
    run()

    assert undertaking.oldcompany_verified is True
    assert undertaking.oldcompany_id is None
    assert undertaking.oldcompany_account is None
    assert undertaking.oldcompany_extid is None
