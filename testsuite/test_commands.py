import ast
import json
import sys

from io import StringIO
from contextlib import redirect_stdout
from datetime import datetime, timedelta

from cache_registry import models
from cache_registry.sync.commands import (
    update_undertakings,
    print_all_undertakings,
    get_last_update
)

from cache_registry.manager import check_integrity, check_passed
from cache_registry.match import flush, manual, unverify, verify
from cache_registry.models import OldCompany, OldCompanyLink, Undertaking, db
from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods
from cache_registry.sync.parsers import parse_company
from instance.settings import FGAS


from .factories import (
    CountryFactory,
    AddressFactory,
    RepresentativeFactory,
    OldCompanyFactory,
    OldCompanyLinkFactory,
    UndertakingFactory,
    UserFactory,
)


def test_update_undertakings_fgas(client):
    with open('testsuite/fixtures/companies-fgas.json') as file:
        data = json.load(file)

    (undertakings_with_changed_represent, undertakings_count) = update_undertakings(
        data, eea_double_check_fgases
    )

    assert undertakings_count == 4
    assert models.Undertaking.query.fgases().count() == 4
    assert len(undertakings_with_changed_represent) == 3


def test_update_undertakings_ods(client):
    with open('testsuite/fixtures/companies-ods.json') as file:
        data = json.load(file)
        (_, undertakings_count) = update_undertakings(data, eea_double_check_ods)
        assert undertakings_count == len(data)
        assert models.Undertaking.query.ods().count() == len(data)

def test_update_undertaking_represent_history(client):
    represent = RepresentativeFactory()
    undertaking =  UndertakingFactory(external_id=10008, represent=represent)
    with open('testsuite/fixtures/companies-fgas.json') as file:
        data = json.load(file)
    (_, undertakings_count) = update_undertakings(data, eea_double_check_fgases)
    assert undertaking.represent.vatnumber == 'TESTVAT123'

def test_parse_company(client):
    country = dict(code='test code', name='Test Name')
    old_company_data = dict(pk=200,
                            addr_street='Test street',
                            addr_place1='Test address1',
                            addr_place2='Test address2',
                            addr_postalcode='000324',
                            # todo find why this string comes like this from bdr
                            date_registered='2017/03/03 12:54 123456789',
                            country=country)
    parse_company(old_company_data, FGAS)
    old_companies = OldCompany.query.all()
    assert len(old_companies) == 1
    assert old_companies[0].external_id == old_company_data['external_id']

def test_parse_company_update(client):
    country = dict(code='test code', name='Test Name')
    oldcompany = OldCompanyFactory(external_id=200)
    old_company_data = dict(pk=200,
                            addr_street='Test street',
                            addr_place1='Test address1',
                            addr_place2='Test address2',
                            addr_postalcode='000324',
                            # todo find why this string comes like this from bdr
                            date_registered='2017/03/03 12:54 123456789',
                            country=country)
    parse_company(old_company_data, FGAS)
    old_companies = OldCompany.query.all()
    assert len(old_companies) == 1
    assert old_companies[0].external_id == old_company_data['external_id']

def test_print_all_undertakings(client):
    with open('testsuite/fixtures/companies-fgas.json') as file:
        undertakings = json.load(file)
    capturedOutput = StringIO()

    with redirect_stdout(capturedOutput):
        print_all_undertakings(undertakings)
    output = capturedOutput.getvalue()
    assert len(output) > 100


def test_get_last_update(client):
    date_n_days_ago = datetime.now() - timedelta(days=40)
    undertaking = UndertakingFactory(date_updated=date_n_days_ago)
    days = 30

    updated_since = datetime.now().strftime('%d/%m/%Y')
    last_update = get_last_update(updated_since=updated_since,
                                  days=None,
                                  domain=undertaking.domain)
    assert last_update.date() == datetime.now().date()

    last_update = get_last_update(updated_since=None,
                                  days=days,
                                  domain=undertaking.domain)
    assert last_update.date() == (datetime.now() - timedelta(days=30)).date()
    last_update = get_last_update(updated_since=None,
                                  days=-1,
                                  domain=undertaking.domain)
    assert last_update.date() == (undertaking.date_updated - timedelta(days=1)).date()


def test_manager(client):
    user1 = UserFactory(username='test1', email='test@mail.com')
    user2 = UserFactory(username='test2', email='test@mail.com')
    capturedOutput = StringIO()
    sys.stdout = capturedOutput
    check_integrity()
    sys.stdout = sys.__stdout__
    duplicates = ast.literal_eval(capturedOutput.getvalue())
    assert duplicates[user1.email] == [user1.id, user2.id]


def test_command_flush(client):
    oldcompany1 = OldCompanyFactory()
    oldcompany2 = OldCompanyFactory()
    undertaking = UndertakingFactory()
    links = [OldCompanyLinkFactory(undertaking=undertaking, oldcompany=oldcompany1),
             OldCompanyLinkFactory(undertaking=undertaking, oldcompany=oldcompany2)]
    flush()
    assert OldCompanyLink.query.count() == 0


def test_command_unverify(client):
    oldcompany = OldCompanyFactory()
    undertaking = UndertakingFactory(
        oldcompany_verified=True,
        oldcompany_extid=oldcompany.external_id,
        oldcompany=oldcompany, oldcompany_id=oldcompany.id)
    link = OldCompanyLinkFactory(undertaking=undertaking, undertaking_id=undertaking.id,
                                 oldcompany=oldcompany, oldcompany_id=oldcompany.id,
                                 verified=True)
    unverify(undertaking.external_id, undertaking.domain)
    assert undertaking.oldcompany == None
    assert undertaking.oldcompany_extid == None
    assert undertaking.oldcompany_verified == False


def test_command_manual(client):
    oldcompany = OldCompanyFactory()
    undertaking = UndertakingFactory(domain='FGAS')
    manual(undertaking.external_id, undertaking.domain, oldcompany.name)
    assert undertaking.oldcompany == None
    assert undertaking.oldcompany_extid == None
    assert undertaking.oldcompany_verified == True
    assert undertaking.oldcompany_account == oldcompany.name


def test_command_verify(client):
    oldcompany = OldCompanyFactory()
    undertaking = UndertakingFactory(domain='FGAS')
    link = OldCompanyLinkFactory(undertaking=undertaking, oldcompany=oldcompany)
    result = verify(undertaking.external_id, oldcompany.external_id)
    assert result == True
    assert link.verified == True
    assert undertaking.oldcompany == link.oldcompany
    assert undertaking.oldcompany_account == link.oldcompany.account
    assert undertaking.oldcompany_verified == True
    assert undertaking.oldcompany_extid == link.oldcompany.external_id


def test_command_check_passed(client):
    with open('testsuite/fixtures/companies-fgas.json') as file:
        data = json.load(file)

    update_undertakings(data, eea_double_check_fgases)

    for undertaking in Undertaking.query.all():
        undertaking.check_passed = None
        db.session.add(undertaking)
        db.session.commit()

    check_passed()
    undertaking_checks_passed = Undertaking.query.filter_by(external_id=10008).first()
    undertaking_checks_failed = Undertaking.query.filter_by(external_id=10009).first()

    assert undertaking_checks_failed.check_passed == False
    assert undertaking_checks_passed.check_passed == True
