import json

from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods


def test_double_checks_fgases_status(client):
    with open("testsuite/fixtures/bad_fgas_data/company_fgas_bad_status.json") as file:
        data = json.load(file)
    result = eea_double_check_fgases(data)
    assert result is False


def test_double_checks_fgases_types(client):
    with open("testsuite/fixtures/bad_fgas_data/company_fgas_bad_type.json") as file:
        data = json.load(file)
    result = eea_double_check_fgases(data)
    assert result is False


def test_double_checks_fgases_businessprofiles(client):
    with open(
        "testsuite/fixtures/bad_fgas_data/company_fgas_bad_businessprofile.json"
    ) as file:
        data = json.load(file)
    result = eea_double_check_fgases(data)
    assert result is False


def test_double_checks_fgases_domain(client):
    with open("testsuite/fixtures/bad_fgas_data/company_fgas_bad_domain.json") as file:
        data = json.load(file)
    result = eea_double_check_fgases(data)
    assert result is False


def test_double_checks_ods_missing_field(client):
    with open("testsuite/fixtures/bad_ods_data/company_ods_missing_field.json") as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False


def test_double_checks_ods_type(client):
    with open("testsuite/fixtures/bad_ods_data/company_ods_bad_type.json") as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False


def test_double_checks_ods_domain(client):
    with open("testsuite/fixtures/bad_ods_data/company_ods_bad_domain.json") as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False


def test_double_checks_ods_status(client):
    with open("testsuite/fixtures/bad_ods_data/company_ods_bad_status.json") as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False


def test_double_checks_ods_country_type(client):
    with open(
        "testsuite/fixtures/bad_ods_data/company_ods_bad_country_type.json"
    ) as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False


def test_double_checks_ods_contact_persons(client):
    with open(
        "testsuite/fixtures/bad_ods_data/company_ods_missing_contact_persons.json"
    ) as file:
        data = json.load(file)
    result = eea_double_check_ods(data)
    assert result is False
