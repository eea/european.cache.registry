# coding=utf-8
from flask import url_for

from . import factories


def test_undertaking_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list',
                              domain=undertaking.domain))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id

    for field in ['name', 'website', 'phone', 'domain', 'status', 'undertaking_type',
                  'vat', 'types', 'oldcompany_verified', 'oldcompany_account',
                  'oldcompany_extid']:
        assert data[field] == getattr(undertaking, field)

    for date_field in ['date_created', 'date_updated']:
        assert data[date_field] == getattr(undertaking, date_field).strftime('%d/%m/%Y')


def test_undertaking_list_domain_filter(client):
    factories.UndertakingFactory(domain='FGAS')
    undertaking = factories.UndertakingFactory(domain='ODS')
    resp = client.get(url_for('api.company-list',
                              domain='ODS'))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id

    for field in ['name', 'website', 'phone', 'domain', 'status', 'undertaking_type',
                  'vat', 'types', 'oldcompany_verified', 'oldcompany_account',
                  'oldcompany_extid']:
        assert data[field] == getattr(undertaking, field)

    for date_field in ['date_created', 'date_updated']:
        assert data[date_field] == getattr(
            undertaking, date_field).strftime('%d/%m/%Y')


def test_undertaking_list_all(client):
    undertaking = factories.UndertakingFactory()
    undertaking.oldcompany_verified = False
    resp = client.get(url_for('api.company-list-all',
                              domain=undertaking.domain))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_list_all_domain_filter(client):
    factories.UndertakingFactory(domain='FGAS')
    undertaking = factories.UndertakingFactory(domain='ODS')
    undertaking.oldcompany_verified = False
    resp = client.get(url_for('api.company-list-all',
                              domain='ODS'))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_list_vat(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.company-list-by-vat',
                              domain=undertaking.domain,
                              vat=undertaking.vat))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_list_vat_domain_filter(client):
    factories.UndertakingFactory(domain='FGAS')
    undertaking = factories.UndertakingFactory(domain='ODS')
    resp = client.get(url_for('api.company-list-by-vat',
                              vat=undertaking.vat,
                              domain='ODS'))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data['company_id'] == undertaking.external_id


def test_undertaking_details(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id

    for field in ['name', 'website', 'phone', 'domain', 'status', 'undertaking_type',
                  'vat', 'types', 'oldcompany_verified', 'oldcompany_account',
                  'oldcompany_extid']:
        assert data[field] == getattr(undertaking, field)

    assert data['date_created'] == undertaking.date_created.strftime('%d/%m/%Y')
    assert data['representative']['name'] == undertaking.represent.name
    assert data['address']['zipcode'] == undertaking.address.zipcode


def test_undertaking_details_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain='FGAS')
    factories.UndertakingFactory(domain='ODS',
                                 external_id=undertaking.external_id)
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id

    for field in ['name', 'website', 'phone', 'domain', 'status', 'undertaking_type',
                  'vat', 'types', 'oldcompany_verified', 'oldcompany_account',
                  'oldcompany_extid']:
        assert data[field] == getattr(undertaking, field)

    assert data['date_created'] == undertaking.date_created.strftime('%d/%m/%Y')
    assert data['representative']['name'] == undertaking.represent.name
    assert data['address']['zipcode'] == undertaking.address.zipcode


def test_undertaking_details_without_address(client):
    undertaking = factories.UndertakingFactory()
    undertaking.address = None
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['address'] is None


def test_undertaking_details_without_address_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain='FGAS')
    factories.UndertakingFactory(domain='ODS',
                                 external_id=undertaking.external_id)
    undertaking.address = None
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['address'] is None


def test_undertaking_details_without_representative(client):
    undertaking = factories.UndertakingFactory()
    undertaking.represent = None
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['representative'] is None


def test_undertaking_details_without_representative_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain='FGAS')
    factories.UndertakingFactory(domain='ODS',
                                 external_id=undertaking.external_id)
    undertaking.represent = None
    resp = client.get(
        url_for('api.company-detail',
                domain=undertaking.domain,
                pk=undertaking.external_id))
    data = resp.json
    assert data['company_id'] == undertaking.external_id
    assert data['representative'] is None


def test_filter_undertaking(client):
    country_ro = factories.CountryFactory(code='ro')
    address_cn = factories.AddressFactory(country=country_ro)
    represent = factories.RepresentativeFactory(name='Le Representant',
                                                vatnumber=1234,
                                                address=address_cn)
    undertaking = factories.UndertakingFactory(oldcompany_verified=True,
                                               vat='21890',
                                               represent=represent,
                                               external_id=42,
                                               country_code='ro',
                                               domain='FGAS',
                                               country_code_orig='cn',
                                               name='A Good Company Name')
    wrong_data = {
        'id': [43, 44],
        'vat': [21891],
        'name': ['Bad Company', 'Bad Name'],
        'OR_name': ['Orice', 'Bad represent'],
        'countrycode': ['bg', undertaking.country_code]
    }

    good_data = {
        'id': [undertaking.external_id],
        'vat': [undertaking.vat],
        'name': [undertaking.name, 'Good Companyy Name', 'A Good Companyy N'],
        'OR_vat': [1234],
        'OR_name': [undertaking.represent.name, 'Le repreesenta'],
        'countrycode': [undertaking.country_code_orig]
    }

    def _test_params(count, **params):
        resp = client.get(url_for('api.company-filter',
                                  domain='FGAS'), params)
        data = resp.json
        assert data['count'] == count

    for field, values in good_data.items():
        for value in values:
            _test_params(1, **{field: value})

    for field, values in wrong_data.items():
        for value in values:
            _test_params(0, **{field: value})


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
    resp = client.get(url_for('api.user-companies', pk=user.email),
                      expect_errors=True)
    assert resp.status_code == 400


def test_candidates_list(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=False)
    resp = client.get(url_for('api.candidate-list',
                              domain=undertaking.domain))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['company_id'] == undertaking.external_id


def test_noncandidates_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for('api.candidate-non-list',
                              domain=undertaking.domain))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data['name'] == undertaking.name


def test_unverify_link(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=True)
    resp = client.post(url_for('api.candidate-unverify',
                               domain=undertaking.domain,
                               undertaking_id=undertaking.external_id),
                       dict(user='test_user'))
    data = resp.json
    assert data['company_id'] == undertaking.external_id