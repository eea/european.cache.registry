# coding=utf-8
from cache_registry.api.user import UserListView
from cache_registry.api.serializers import AddressDetail
from cache_registry.api.views import ApiView, DetailView, ListView
from cache_registry.models import Auditor


class AuditorListView(ListView):
    model = Auditor

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("address_id",)
        for field in _strip_fields:
            data.pop(field)
        data.update(
            {
                "ms_accreditation_issuing_countries": [
                    country.code for country in obj.ms_accreditation_issuing_countries
                ],
                "address": AddressDetail.serialize(obj.address),
                "users": [UserListView.serialize(cp) for cp in obj.contact_persons],
            }
        )
        return data


class AuditorDetailView(DetailView):
    model = Auditor

    def get_object(self, pk, **kwargs):
        return self.model.query.filter_by(auditor_uid=pk).first_or_404()

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("address_id",)
        for field in _strip_fields:
            data.pop(field)
        data.update(
            {
                "ms_accreditation_issuing_countries": [
                    country.code for country in obj.ms_accreditation_issuing_countries
                ],
                "address": AddressDetail.serialize(obj.address),
                "users": [UserListView.serialize(cp) for cp in obj.contact_persons],
            }
        )
        return data
