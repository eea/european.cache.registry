# coding=utf-8
import json

from functools import reduce
from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import (
    Undertaking, Stock, db
)


class StocksUndertakingListView(ApiView):
    model = Stock

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj, pop_id=False)
        _strip_fields = (
            'undertaking_id',
            'year'
        )
        for field in _strip_fields:
            data.pop(field)
        return data

    def post(self, **kwargs):
        external_id = kwargs['external_id']
        undertaking = Undertaking.query.filter_by(external_id=external_id, domain='ODS').first()
        if not undertaking:
            context = {}
            context[external_id] = {}
            return context
        years = [stock.year for stock in Stock.query.filter_by(undertaking=undertaking).distinct(Stock.year).all()]
        context = {}
        context[external_id] = {}
        for year in years:
            context[external_id][year] = [self.serialize(u) for u in undertaking.stocks.filter_by(year=year).all()]
        return context


class StocksYearListView(ListView):
    model = Stock

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj, pop_id=False)
        _strip_fields = (
            'undertaking_id',
            'year'
        )
        for field in _strip_fields:
            data.pop(field)
        return data

    def post(self, **kwargs):

        year = kwargs['year']
        stocks = Stock.query.filter_by(year=year).all()
        context = {
            'year': [self.serialize(u) for u in stocks]
        }
        return context

class StockListing(ListView):
    model = Stock

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj, pop_id=False)
        _strip_fields = (
            'undertaking_id',
        )
        for field in _strip_fields:
            data.pop(field)
        data['company_id'] =obj.undertaking.external_id
        data['company_name'] = obj.undertaking.name
        return data

class LoadStocksJson(ApiView):
    model = Stock

    def post(self, **kwargs):
        file = request.files.get('file', None)
        context = {'message': ""}
        if not file:
            context['message'] = "No file uploaded."
            return context
        json_data = file.read()
        data = json.loads(json_data)
        for stock in data:
            undertaking = Undertaking.query.filter_by(external_id=stock['company_id'], domain='ODS').first()
            if not undertaking:
                context['message'] = "\n".join(
                    [context['message'],
                    "Company {} does not exist.".format(stock['company_id'])]
                )
                continue
            stock_object = Stock.query.filter_by(
                year=stock['year'],
                substance_name_form=stock['substance_name_form'],
                undertaking_id=undertaking.id,
                type=stock['type']).first()
            if not stock_object:
                stock_object = Stock(
                    year=stock['year'],
                    type=stock['type'],
                    substance_name_form=stock['substance_name_form'],
                    code=str(stock['company_id']),
                    result=stock['result'],
                    is_virgin=stock['is_virgin'],
                    undertaking=undertaking,
                    undertaking_id=undertaking.id,
                )
                db.session.add(stock_object)
                db.session.commit()
            else:
                stock_object.result = stock['result']
                stock_object.type = stock['type']
                stock_object.is_virgin = stock['is_virgin']

        if not context['message']:
            context['message'] = 'All stocks were imported succesfully.'

        return context

    def get(self, **kwargs):
        # return a dummy with the JSON structure.
        context = [
            {
                "year": 2019,
                "type": "Type name 1",
                "substance_name_form": "Substance name 1",
                "is_virgin": True,
                "company_id": '12345',
                "result": 1400,
            },
            {
                "year": 2020,
                "type": "Type name 2",
                "substance_name_form": "Substance name 2",
                "is_virgin": True,
                "company_id": '67849',
                "result": 3200,
            }
        ]
        return context
