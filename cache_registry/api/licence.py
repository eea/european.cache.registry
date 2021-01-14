# coding=utf-8
from functools import reduce
import json

from flask import current_app
from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import (
    DeliveryLicence, Licence,
    Substance, Undertaking,
)


class SubstanceYearListView(ApiView):
    model = Substance

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first_or_404()
        substances = undertaking.deliveries.filter_by(year=year).first()
        if not substances:
            return []
        substances = substances.substances
        data = json.loads(request.data)
        if data.get('substances'):
            substances = self.filter_substances(data['substances'], substances)
        if data.get('actions'):
            substances = self.filter_type(data['actions'], substances)
        return substances.all()

    def filter_substances(self, substances, substances_objects):
        return substances_objects.filter(Substance.substance.in_(substances))

    def filter_type(self, actions, substances_objects):
        return substances_objects.filter(Substance.lic_type.in_(actions))

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'date_created', 'date_updated',
            'delivery_id'
        )
        for field in _strip_fields:
            data.pop(field)
        data['company_id'] = obj.deliverylicence.undertaking.external_id
        data['use_kind'] = data.pop('lic_use_kind')
        data['use_desc'] = data.pop('lic_use_desc')
        data['type'] = data.pop('lic_type')
        data['quantity'] = int(data['quantity'])
        return data

    def patch_licences(self, **kwargs):
        data = []
        year = int(kwargs['year'])
        pk = int(kwargs['pk'])
        patch = current_app.config.get('PATCH_LICENCES', [])
        for element in patch:
            if element.get('year') == year and element.get('company_id') == pk:
                data.append(element)
        return data

    def post(self, **kwargs):
        data = [self.serialize(u) for u in self.get_queryset(**kwargs)]
        data.extend(self.patch_licences(**kwargs))
        return {"licences": data}


class LicencesOfOneDeliveryListView(ListView):
    model = Licence

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first_or_404()
        delivery = undertaking.deliveries.filter_by(year=year).first_or_404()
        substances = delivery.substances.all()
        licences = [substance.licences.all() for substance in substances]
        return reduce(lambda x,y: x+y,licences)


class SubstancesOfOneDeliveryListView(ListView):
    model = Substance

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first_or_404()
        delivery = undertaking.deliveries.filter_by(year=year).first_or_404()
        substances = delivery.substances.all()
        return substances
