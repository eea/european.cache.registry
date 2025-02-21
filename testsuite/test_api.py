# coding=utf-8
import json
from datetime import datetime

from flask import url_for

from cache_registry.models import db
from instance.settings import FGAS, ODS
from testsuite import factories


def test_authorization_failed(client):
    resp = client.get(
        url_for("api.company-list", domain="FGAS"),
        headers={"Authorization": "test"},
        expect_errors=True,
    )
    assert resp.status_code == 401
    assert resp.json["status"] == "Unauthorized"


def test_auditor_list(client):
    auditor = factories.AuditorFactory()
    resp = client.get(url_for("api.auditor-list"))
    assert len(resp.json) == 1

    data = resp.json[0]
    assert data["auditor_uid"] == auditor.auditor_uid
    assert data["name"] == auditor.name
    assert data["status"] == auditor.status
    assert data["website"] == auditor.website
    assert data["phone"] == auditor.phone
    for date_field in ("date_created", "date_updated", "date_created_in_ecr"):
        assert data[date_field] == getattr(auditor, date_field).strftime("%d/%m/%Y")
    assert data["ets_accreditation"] == auditor.ets_accreditation
    assert data["ms_accreditation"] == auditor.ms_accreditation
    assert data["ms_accreditation_issuing_countries"] == [
        country.code for country in auditor.ms_accreditation_issuing_countries
    ]
    assert data["address"]["street"] == auditor.address.street
    assert data["address"]["number"] == auditor.address.number
    assert data["address"]["city"] == auditor.address.city
    assert data["address"]["zipcode"] == auditor.address.zipcode
    assert data["address"]["country"]["code"] == auditor.address.country.code


def test_auditor_details(client):
    auditor = factories.AuditorFactory()
    resp = client.get(url_for("api.auditor-detail", pk=auditor.auditor_uid))

    data = resp.json
    assert data["auditor_uid"] == auditor.auditor_uid
    assert data["name"] == auditor.name
    assert data["status"] == auditor.status
    assert data["website"] == auditor.website
    assert data["phone"] == auditor.phone
    for date_field in ("date_created", "date_updated", "date_created_in_ecr"):
        assert data[date_field] == getattr(auditor, date_field).strftime("%d/%m/%Y")
    assert data["ets_accreditation"] == auditor.ets_accreditation
    assert data["ms_accreditation"] == auditor.ms_accreditation
    assert data["ms_accreditation_issuing_countries"] == [
        country.code for country in auditor.ms_accreditation_issuing_countries
    ]
    assert data["address"]["street"] == auditor.address.street
    assert data["address"]["number"] == auditor.address.number
    assert data["address"]["city"] == auditor.address.city
    assert data["address"]["zipcode"] == auditor.address.zipcode
    assert data["address"]["country"]["code"] == auditor.address.country.code


def test_auditor_check(client):
    undertaking = factories.UndertakingFactory()
    undertaking.country_code = undertaking.address.country.code
    db.session.add(undertaking)
    db.session.commit()
    auditor = factories.AuditorFactory(address__country=undertaking.address.country)
    resp = client.get(
        url_for(
            "api.company-auditor_check",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        )
    )
    data = resp.json
    assert data["access"] is True
    assert data["auditor"]["auditor_uid"] == auditor.auditor_uid
    assert data["auditor"]["name"] == auditor.name


def test_auditor_check_fail(client):
    undertaking = factories.UndertakingFactory()
    undertaking.country_code = undertaking.address.country.code
    db.session.add(undertaking)
    db.session.commit()
    other_country = factories.CountryFactory(code="RO")
    auditor = factories.AuditorFactory(address__country=other_country)

    # Only FGAS domain is accepted
    resp = client.get(
        url_for(
            "api.company-auditor_check",
            domain="ODS",
            external_id=12345,
            auditor_uid=3234,
        )
    )
    assert resp.status_code == 200
    data = resp.json
    assert data == {"error": "Invalid domain"}

    # Auditor not found or undertaking not found
    resp = client.get(
        url_for(
            "api.company-auditor_check",
            domain=undertaking.domain,
            external_id=34234,
            auditor_uid=43243,
        ),
        expect_errors=True,
    )

    assert resp.status_code == 404

    resp = client.get(
        url_for(
            "api.company-auditor_check",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        )
    )
    assert resp.status_code == 200
    data = resp.json
    assert data == {"access": False, "auditor": None}


def test_auditor_assign(client):
    undertaking = factories.UndertakingFactory()
    undertaking.country_code = undertaking.address.country.code
    db.session.add(undertaking)
    db.session.commit()
    auditor = factories.AuditorFactory()
    user = factories.UserFactory(email="test@mail.com")
    auditor.contact_persons.append(user)
    db.session.commit()
    resp = client.post(
        url_for(
            "api.company-auditor_assign",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        ),
        json.dumps(
            {
                "email": user.email,
                "reporting_envelope_url": "reporting",
                "verification_envelope_url": "verification",
            }
        ),
        content_type="application/json",
    )
    data = resp.json
    assert data["success"] is True

    # test if information can be retrieved in Auditor detail endpoint
    resp = client.get(url_for("api.auditor-detail", pk=auditor.auditor_uid))
    data = resp.json
    assert data["auditor_uid"] == auditor.auditor_uid
    assert len(data["audited_companies"]) == 1
    audited_company = data["audited_companies"][0]
    assert audited_company["start_date"] == datetime.now().strftime("%d/%m/%Y")
    assert audited_company["end_date"] is None
    assert audited_company["reporting_envelope_url"] == "reporting"
    assert audited_company["verification_envelope_url"] == "verification"
    assert audited_company["undertaking"]["company_id"] == undertaking.external_id
    assert audited_company["undertaking"]["domain"] == undertaking.domain
    assert audited_company["undertaking"]["name"] == undertaking.name
    assert audited_company["auditor"]["auditor_uid"] == auditor.auditor_uid
    assert audited_company["auditor"]["name"] == auditor.name
    assert audited_company["user"]["email"] == user.email
    assert audited_company["user"]["username"] == user.username
    assert audited_company["user"]["first_name"] == user.first_name
    assert audited_company["user"]["last_name"] == user.last_name
    assert audited_company["user"]["type"] == user.type

    # test if information can be retrieved in Undertaking detail endpoint
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    assert len(data["auditors"]) == 1
    auditor_company = data["auditors"][0]
    assert auditor_company["start_date"] == datetime.now().strftime("%d/%m/%Y")
    assert auditor_company["end_date"] is None
    assert auditor_company["reporting_envelope_url"] == "reporting"
    assert auditor_company["verification_envelope_url"] == "verification"
    assert auditor_company["auditor"]["auditor_uid"] == auditor.auditor_uid
    assert auditor_company["auditor"]["name"] == auditor.name
    assert auditor_company["undertaking"]["company_id"] == undertaking.external_id
    assert auditor_company["undertaking"]["domain"] == undertaking.domain
    assert auditor_company["undertaking"]["name"] == undertaking.name
    assert auditor_company["user"]["email"] == user.email
    assert auditor_company["user"]["username"] == user.username
    assert auditor_company["user"]["first_name"] == user.first_name
    assert auditor_company["user"]["last_name"] == user.last_name
    assert auditor_company["user"]["type"] == user.type


def test_auditor_assign_fail_validation(client):
    undertaking = factories.UndertakingFactory()
    undertaking.country_code = undertaking.address.country.code
    db.session.add(undertaking)
    db.session.commit()
    auditor = factories.AuditorFactory()
    user = factories.UserFactory(email="email@test.com")

    resp = client.post(
        url_for(
            "api.company-auditor_assign",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        ),
        json.dumps(
            {
                "email": user.email,
            }
        ),
        content_type="application/json",
        expect_errors=True,
    )

    assert resp.status_code == 400
    data = resp.json
    assert data["errors"] == {
        "email": ["User not found"],
        "reporting_envelope_url": ["Reporting envelope URL is required"],
        "verification_envelope_url": ["Verification envelope URL is required"],
    }

    auditor.contact_persons.append(user)
    db.session.commit()

    factories.AuditorUndertakingFactory(
        undertaking=undertaking,
        auditor=auditor,
        user=user,
        start_date=datetime.now(),
        end_date=None,
        reporting_envelope_url="reporting",
        verification_envelope_url="verification",
    )
    resp = client.post(
        url_for(
            "api.company-auditor_assign",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        ),
        json.dumps(
            {
                "email": user.email,
                "reporting_envelope_url": "reporting",
                "verification_envelope_url": "verification",
            }
        ),
        content_type="application/json",
        expect_errors=True,
    )
    assert resp.status_code == 400
    data = resp.json
    assert data["errors"] == {
        "auditor": ["Auditor already assigned"],
    }


def test_auditor_unassign(client):
    undertaking = factories.UndertakingFactory()
    undertaking.country_code = undertaking.address.country.code
    db.session.add(undertaking)
    db.session.commit()
    auditor = factories.AuditorFactory()
    user = factories.UserFactory(email="test@mail.com")
    auditor.contact_persons.append(user)
    db.session.commit()
    auditor_undertaking = factories.AuditorUndertakingFactory(
        auditor=auditor,
        undertaking=undertaking,
        user=user,
        start_date=datetime.now(),
        end_date=None,
        reporting_envelope_url="reporting",
        verification_envelope_url="verification",
    )
    resp = client.post(
        url_for(
            "api.company-auditor_unassign",
            domain=undertaking.domain,
            external_id=undertaking.external_id,
            auditor_uid=auditor.auditor_uid,
        ),
        json.dumps(
            {
                "email": user.email,
                "reporting_envelope_url": "reporting",
                "verification_envelope_url": "verification",
            }
        ),
        content_type="application/json",
    )
    assert resp.status_code == 200
    data = resp.json
    assert data["success"] is True
    assert auditor_undertaking.end_date == datetime.now().date()


def test_undertaking_list(client):
    undertaking = factories.UndertakingFactory()
    type = factories.TypeFactory(domain=undertaking.domain, type="IMPORTER")
    undertaking.types.append(type)
    resp = client.get(url_for("api.company-list", domain=undertaking.domain))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id
    for field in [
        "name",
        "website",
        "phone",
        "domain",
        "status",
        "undertaking_type",
        "vat",
        "oldcompany_verified",
        "oldcompany_account",
        "oldcompany_extid",
    ]:
        assert data[field] == getattr(undertaking, field)

    assert data["types"] == type.type

    for date_field in ["date_created", "date_updated"]:
        assert data[date_field] == getattr(undertaking, date_field).strftime("%d/%m/%Y")


def test_undertaking_list_small(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for("api.company-list-small", domain=undertaking.domain))

    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id
    for field in ["name", "domain", "vat"]:
        assert data[field] == getattr(undertaking, field)
    assert data["date_created"] == getattr(undertaking, "date_created").strftime(
        "%d/%m/%Y"
    )


def test_undertaking_detail_short_view(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(
        url_for(
            "api.company-detail_short",
            domain=undertaking.domain,
            pk=undertaking.external_id,
        )
    )

    resp_data = resp.json
    assert len(resp_data) == 8
    data = resp_data
    assert data["company_id"] == undertaking.external_id
    assert data["company_name"] == undertaking.name
    assert (
        data["address"]
        == undertaking.address.street + ", " + undertaking.address.number
    )
    assert data["postal_code"] == undertaking.address.zipcode
    assert data["city"] == undertaking.address.city
    assert data["country"] == undertaking.address.country.name
    assert data["eori_code"] == undertaking.vat


def test_undertaking_list_small_none(client):
    resp = client.get(url_for("api.company-list-small", domain="FGAS"))

    resp_data = resp.json
    assert len(resp_data) == 0


def test_undertaking_list_domain_filter(client):
    factories.UndertakingFactory(domain=FGAS)
    undertaking = factories.UndertakingFactory(domain=ODS)
    type = factories.TypeFactory(domain=undertaking.domain, type="IMPORTER")
    undertaking.types.append(type)
    resp = client.get(url_for("api.company-list", domain=ODS))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id

    for field in [
        "name",
        "website",
        "phone",
        "domain",
        "status",
        "undertaking_type",
        "vat",
        "oldcompany_verified",
        "oldcompany_account",
        "oldcompany_extid",
    ]:
        assert data[field] == getattr(undertaking, field)
    assert data["types"] == type.type

    for date_field in ["date_created", "date_updated"]:
        assert data[date_field] == getattr(undertaking, date_field).strftime("%d/%m/%Y")


def test_undertaking_list_all(client):
    undertaking = factories.UndertakingFactory()
    undertaking.oldcompany_verified = False
    resp = client.get(url_for("api.company-list-all", domain=undertaking.domain))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id


def test_undertaking_list_all_domain_filter(client):
    factories.UndertakingFactory(domain=FGAS)
    undertaking = factories.UndertakingFactory(domain=ODS)
    undertaking.oldcompany_verified = False
    resp = client.get(url_for("api.company-list-all", domain=ODS))
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id


def test_undertaking_list_vat(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(
        url_for(
            "api.company-list-by-vat", domain=undertaking.domain, vat=undertaking.vat
        )
    )
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id


def test_undertaking_list_vat_domain_filter(client):
    factories.UndertakingFactory(domain=FGAS)
    undertaking = factories.UndertakingFactory(domain=ODS)
    resp = client.get(
        url_for("api.company-list-by-vat", vat=undertaking.vat, domain=ODS)
    )
    resp_data = resp.json
    assert len(resp_data) == 1
    data = resp_data[0]
    assert data["company_id"] == undertaking.external_id


def test_undertaking_details(client):
    undertaking = factories.UndertakingFactory(oldcompany=None)
    type = factories.TypeFactory(domain=undertaking.domain, type="EXPORTER")
    undertaking.types.append(type)
    oldcompany = factories.OldCompanyFactory(id=2)
    factories.OldCompanyLinkFactory(oldcompany=oldcompany, undertaking=undertaking)
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    for field in [
        "name",
        "website",
        "phone",
        "domain",
        "status",
        "undertaking_type",
        "vat",
        "oldcompany_verified",
        "oldcompany_account",
        "oldcompany_extid",
    ]:
        assert data[field] == getattr(undertaking, field)

    assert data["date_created"] == undertaking.date_created.strftime("%d/%m/%Y")
    assert data["representative"]["name"] == undertaking.represent.name
    assert data["address"]["zipcode"] == undertaking.address.zipcode
    assert data["candidates"][0]["company_id"] == oldcompany.external_id
    assert data["types"] == type.type


def test_undertaking_details_404(client):
    resp = client.get(
        url_for("api.company-detail", domain="ODS", pk=1), expect_errors=True
    )
    assert resp.status_code == 404


def test_undertaking_details_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain=FGAS)
    factories.UndertakingFactory(domain=ODS, external_id=undertaking.external_id)
    type = factories.TypeFactory(domain=ODS, type="EXPORTER")
    undertaking.types.append(type)
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    for field in [
        "name",
        "website",
        "phone",
        "domain",
        "status",
        "undertaking_type",
        "vat",
        "oldcompany_verified",
        "oldcompany_account",
        "oldcompany_extid",
    ]:
        assert data[field] == getattr(undertaking, field)

    assert data["date_created"] == undertaking.date_created.strftime("%d/%m/%Y")
    assert data["representative"]["name"] == undertaking.represent.name
    assert data["address"]["zipcode"] == undertaking.address.zipcode
    assert data["types"] == type.type


def test_undertaking_details_without_address(client):
    undertaking = factories.UndertakingFactory()
    undertaking.address = None
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    assert data["address"] is None


def test_undertaking_details_without_address_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain=FGAS)
    factories.UndertakingFactory(domain=ODS, external_id=undertaking.external_id)
    undertaking.address = None
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    assert data["address"] is None


def test_undertaking_details_without_representative(client):
    undertaking = factories.UndertakingFactory()
    undertaking.represent = None
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    assert data["representative"] is None


def test_undertaking_details_without_representative_domain_filter(client):
    undertaking = factories.UndertakingFactory(domain=FGAS)
    factories.UndertakingFactory(domain=ODS, external_id=undertaking.external_id)
    undertaking.represent = None
    resp = client.get(
        url_for(
            "api.company-detail", domain=undertaking.domain, pk=undertaking.external_id
        )
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id
    assert data["representative"] is None


def test_filter_undertaking(client):
    country_ro = factories.CountryFactory(code="ro")
    address_cn = factories.AddressFactory(country=country_ro)
    represent = factories.RepresentativeFactory(
        name="Le Representant", vatnumber=1234, address=address_cn
    )
    undertaking = factories.UndertakingFactory(
        oldcompany_verified=True,
        vat="21890",
        represent=represent,
        external_id=42,
        country_code="ro",
        domain=FGAS,
        country_code_orig="cn",
        name="A Good Company Name",
    )
    wrong_data = {
        "id": [43, 44],
        "vat": [21891],
        "name": ["Bad Company", "Bad Name"],
        "OR_name": ["Orice", "Bad represent"],
        "countrycode": ["bg", undertaking.country_code],
    }

    good_data = {
        "id": [undertaking.external_id],
        "vat": [undertaking.vat],
        "name": [undertaking.name, "Good Companyy Name", "A Good Companyy N"],
        "OR_vat": [1234],
        "OR_name": [undertaking.represent.name, "Le repreesenta"],
        "countrycode": [undertaking.country_code_orig],
    }

    def _test_params(count, **params):
        resp = client.get(url_for("api.company-filter", domain=FGAS), params)
        data = resp.json
        assert data["count"] == count

    for field, values in good_data.items():
        for value in values:
            _test_params(1, **{field: value})

    for field, values in wrong_data.items():
        for value in values:
            _test_params(0, **{field: value})


def test_user_list(client):
    user = factories.UserFactory()
    resp = client.get(url_for("api.user-list"))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data["username"] == user.username


def test_user_companies_by_username(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for("api.user-companies", pk=user.username))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data["company_id"] == undertaking.external_id


def test_user_companies_404(client):
    resp = client.get(url_for("api.user-companies", pk=20), expect_errors=True)
    assert resp.status_code == 404


def test_user_companies_by_email(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory()
    undertaking.contact_persons.append(user)
    resp = client.get(url_for("api.user-companies", pk=user.email), expect_errors=True)
    assert resp.status_code == 404


def test_user_companies_include_ecas(client):
    undertaking = factories.UndertakingFactory()
    user = factories.UserFactory(ecas_id="username", username="username@mail.com")
    undertaking.contact_persons.append(user)
    resp = client.get(url_for("api.user-companies_ecas"), {"ecas_id": user.ecas_id})
    assert resp.status_code == 200
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data["company_id"] == undertaking.external_id


def test_candidates_list(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=False)
    oldcompany = factories.OldCompanyFactory(id=2)
    factories.OldCompanyLinkFactory(oldcompany=oldcompany, undertaking=undertaking)
    resp = client.get(url_for("api.candidate-list", domain=undertaking.domain))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data["undertaking"]["company_id"] == undertaking.external_id
    assert len(data["links"]) == 1
    assert data["links"][0]["name"] == oldcompany.name


def test_noncandidates_list(client):
    undertaking = factories.UndertakingFactory()
    resp = client.get(url_for("api.candidate-non-list", domain=undertaking.domain))
    data = resp.json
    assert len(data) == 1
    data = data[0]
    assert data["name"] == undertaking.name


def test_unverify_link(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=True)
    factories.OldCompanyLinkFactory(
        oldcompany=undertaking.oldcompany, undertaking=undertaking
    )
    resp = client.post(
        url_for(
            "api.candidate-unverify",
            domain=undertaking.domain,
            undertaking_id=undertaking.external_id,
        ),
        dict(user="test_user"),
    )
    data = resp.json
    assert data["company_id"] == undertaking.external_id


def test_verify_none_link(client):
    undertaking = factories.UndertakingFactory(oldcompany_verified=True)
    factories.OldCompanyLinkFactory(
        oldcompany=undertaking.oldcompany, undertaking=undertaking
    )

    client.post(
        url_for(
            "api.candidate-verify-none",
            domain=undertaking.domain,
            undertaking_id=undertaking.external_id,
        ),
        dict(user="test_user", id=1, verified=True),
    )
    assert undertaking.oldcompany is None
    assert undertaking.oldcompany_verified is True
    assert undertaking.oldcompany_extid is None


def test_verify_manual(client):

    oldcompany = factories.OldCompanyFactory(account="test_account")
    undertaking = factories.UndertakingFactory()

    client.post(
        url_for(
            "api.candidate-manual",
            domain=undertaking.domain,
            undertaking_id=undertaking.external_id,
            oldcompany_account=oldcompany.account,
        ),
        dict(user="test_user"),
    )
    assert undertaking.oldcompany is None
    assert undertaking.oldcompany_verified is True
    assert undertaking.oldcompany_extid is None
    assert undertaking.oldcompany_account == oldcompany.account


def test_update_status_undertaking(client):
    undertaking = factories.UndertakingFactory(status="DISABLED")
    resp = client.post(
        url_for(
            "api.company-statusupdate",
            domain=undertaking.domain,
            pk=undertaking.external_id,
        ),
        dict(status="VALID"),
    )
    assert json.loads(resp.body.decode())
    assert undertaking.status == "VALID"


def test_update_status_undertaking_no_status(client):
    undertaking = factories.UndertakingFactory(status="DISABLED")
    resp = client.post(
        url_for(
            "api.company-statusupdate",
            domain=undertaking.domain,
            pk=undertaking.external_id,
        ),
        dict(status=""),
    )
    assert resp.body.decode() == "false"
