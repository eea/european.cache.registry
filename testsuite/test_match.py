# coding=utf8

import requests

from flask import url_for
from . import factories
from flask import current_app


from cache_registry.match import run
from cache_registry.models import OldCompanyLink, Undertaking, OldCompany


def mockreturn(url, **kwargs):
    res = requests.Response()
    res.status_code = 200
    res.headers['contenttype'] = 'application/json'
    res._content = '{"message": "mess", "status": "success"}'
    return res


def test_verify_link(client, monkeypatch):

    monkeypatch.setattr(requests, 'get', mockreturn)
    undertaking = factories.UndertakingFactory(oldcompany=None)
    oldcompany = factories.OldCompanyFactory()
    factories.OldCompanyLinkFactory(oldcompany=oldcompany,
                                    undertaking=undertaking)
    client.post(url_for('api.candidate-verify',
                        domain=undertaking.domain,
                        undertaking_id=undertaking.external_id,
                        oldcompany_id=oldcompany.external_id),
                dict(user='test_user'))
    resp = client.get(url_for('misc.log-matching', domain=undertaking.domain))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['verified'] is True
    assert data['company_id'] == undertaking.external_id
    assert data['oldcompany_id'] == oldcompany.external_id
    assert data['user'] == 'test_user'
    assert data['oldcompany_account'] == oldcompany.account


def test_auto_verify_companies(client, monkeypatch):
    monkeypatch.setattr(requests, 'get', mockreturn)
    old_company = factories.OldCompanyFactory(country_code='FR')
    undertaking = factories.UndertakingFactory(oldcompany=old_company,
                                               country_code='FR',
                                               vat='1234',
                                               oldcompany_verified=False)
    runner = current_app.test_cli_runner()
    results = runner.invoke(run, [])
    undertaking = Undertaking.query.first()
    assert undertaking.oldcompany_verified is True
    assert undertaking.oldcompany_id is None
    assert undertaking.oldcompany_account is None
    assert undertaking.oldcompany_extid is None


def test_find_company_link(client, monkeypatch):
    monkeypatch.setattr(requests, 'get', mockreturn)
    undertaking = factories.UndertakingFactory(country_code='FR',
                                               vat='1234',
                                               oldcompany_verified=False)
    old_company = factories.OldCompanyFactory(
        country_code=undertaking.country_code,
        eori=undertaking.vat
    )
    runner = current_app.test_cli_runner()
    results = runner.invoke(run, [])
    undertaking = Undertaking.query.first()
    old_company = OldCompany.query.filter_by(eori=undertaking.vat).first()
    links = OldCompanyLink.query.all()
    assert len(links) == 1
    assert not links[0].verified
    assert links[0].undertaking_id == undertaking.id
    assert links[0].oldcompany_id == old_company.id
