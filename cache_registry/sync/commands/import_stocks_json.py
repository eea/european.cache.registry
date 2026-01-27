import click
import json

from cache_registry.models import (
    db,
    Stock,
    Undertaking,
)
from cache_registry.sync import sync_manager


@sync_manager.command("import_stocks_json")
@click.option("-f", "--file", "file", help="Json file with stocks")
def import_stocks_json(file):
    with open(file) as f:
        json_data = f.read()
        data = json.loads(json_data)

    for stock in data:
        code = stock["code"]
        try:
            int(code)
            undertaking = Undertaking.query.filter_by(external_id=code).first()
        except ValueError:
            undertaking = Undertaking.query.filter_by(oldcompany_account=code).first()
        if not undertaking:
            year = stock["year"]
            substance_name_form = stock["substance_name_form"]
            code = stock["code"]
            type = stock["type"]
            print(
                f"Stock {year} - {substance_name_form} - {code} - {type} \
                 was not imported as undertaking does not exist."
            )
            continue
        stock_object = Stock.query.filter_by(
            year=stock["year"],
            substance_name_form=stock["substance_name_form"],
            code=stock["code"],
            type=stock["type"],
        ).first()
        if not stock_object:
            stock_object = Stock(
                year=stock["year"],
                substance_name_form=stock["substance_name_form"],
                code=stock["code"],
                is_virgin=bool(stock["is_virgin"]),
                result=stock["result"],
                type=stock["type"],
                undertaking_id=undertaking.id,
                undertaking=undertaking,
            )
            db.session.add(stock_object)
            db.session.commit()
        else:
            stock_object.is_virgin = bool(stock["is_virgin"])
            stock_object.result = stock["result"]
            stock_object.type = stock["type"]
            db.session.add(stock_object)
            db.session.commit()
