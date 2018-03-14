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

from cache_registry.manager import check_integrity
from cache_registry.models import OldCompany
from cache_registry.sync.fgases import eea_double_check_fgases
from cache_registry.sync.ods import eea_double_check_ods
from cache_registry.sync.parsers import parse_company
from instance.settings import FGAS


from .factories import (
    CountryFactory,
    AddressFactory,
    UndertakingFactory,
    UserFactory,
)


def test_update_undertakings_fgas(client):
    with open('testsuite/fixtures/companies-fgas.json') as file:
        data = json.load(file)
    undertakings_count = update_undertakings(data, eea_double_check_fgases)
    assert undertakings_count == 2
    assert models.Undertaking.query.fgases().count() == 2


def test_update_undertakings_ods(client):
    with open('testsuite/fixtures/companies-ods.json') as file:
        data = json.load(file)
        undertakings_count = update_undertakings(data, eea_double_check_ods)
        assert undertakings_count == len(data)
        assert models.Undertaking.query.ods().count() == len(data)


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
