# coding=utf-8

from cache_registry.api.views import ListView
from cache_registry.models import (
    DeliveryLicence, Licence,
    Undertaking,
)


class LicenceYearListView(ListView):
    model = Licence

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first()
        return undertaking.deliveries.filter_by(year=year, current=True).first().licences.all()


class LicenceYearAllDeliveriesListView(ListView):
    model = Licence

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first()
        return undertaking.deliveries.filter_by(year=year).order_by(DeliveryLicence.order)


class LicencesOfOneDeliveryListView(ListView):
    model = Licence

    def get_queryset(self, domain, pk, year, delivery_name, **kwargs):
        undertaking = Undertaking.query.filter_by(domain=domain, external_id=pk).first()
        return undertaking.deliveries.filter_by(year=year, name=delivery_name).first().licences.all()