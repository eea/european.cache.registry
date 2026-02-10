import click
import json
import requests
import urllib.parse

from datetime import datetime
from io import BytesIO
from scrapy.selector import Selector
from urllib.request import urlopen
from zipfile import ZipFile

from flask import current_app

from cache_registry.models import (
    db,
    Stock,
    Undertaking,
)
from cache_registry.sync import sync_manager


@sync_manager.command("stocks")
@click.option("-y", "--year", "year", help="Year to use")
def stocks(year=None):
    return call_stocks(year)


def _update_or_create_stocks(data, undertaking):
    created = False
    stock = Stock.query.filter_by(
        year=data["year"],
        type=data["type"],
        substance_name_form=data["substance_name_form"],
        undertaking=undertaking,
        code=str(undertaking.external_id),
        undertaking_id=undertaking.id,
    ).first()
    if stock:
        stock.is_virgin = data["is_virgin"]
        stock.result = data["result"]
    else:
        stock = Stock(
            year=data["year"],
            type=data["type"],
            substance_name_form=data["substance_name_form"],
            is_virgin=data["is_virgin"],
            result=data["result"],
            code=str(undertaking.external_id),
            undertaking=undertaking,
            undertaking_id=undertaking.id,
        )
        created = True
    db.session.add(stock)
    db.session.commit()
    return stock, created


def call_stocks(year=None):
    if year:
        year = int(year)
    else:
        year = datetime.now().year
    include_test_data = current_app.config.get("STOCKS_INCLUDE_TESTDATA", "No")
    params = urllib.parse.urlencode(
        {
            "opt_showresult": "false",
            "opt_servicemode": "sync",
            "Upper_limit": year,
            "Include_testdata": include_test_data,
        }
    )
    url = "?".join([current_app.config.get("STOCKS_API_URL", ""), params])
    headers = {"Authorization": current_app.config.get("STOCKS_API_TOKEN", "")}
    ssl_verify = current_app.config["HTTPS_VERIFY"]
    response = requests.get(url, headers=headers, verify=ssl_verify)
    a_href = Selector(response=response).xpath("//a/@href").get()
    resp_file = urlopen(a_href)
    data = resp_file.read()

    myzip = ZipFile(BytesIO(data))
    file_name = myzip.namelist()[0]
    res = myzip.open(file_name).read()
    json_data = json.loads(res)
    stocks = Stock.query.all()
    stocks_count = len(stocks)
    for stock in stocks:
        db.session.delete(stock)
    print(f"Deleted {stocks_count} stocks")
    stocks_count = 0
    for stock in json_data:
        if stock["company_id"].startswith("ods"):
            undertaking = Undertaking.query.filter_by(
                oldcompany_account=stock["company_id"], domain="ODS"
            ).first()
        else:
            undertaking = Undertaking.query.filter_by(
                external_id=stock["company_id"], domain="ODS"
            ).first()
        if undertaking:
            stock, created = _update_or_create_stocks(stock, undertaking)
            if created:
                stocks_count += 1
    print(f"Created {stocks_count} stocks")
    return True
