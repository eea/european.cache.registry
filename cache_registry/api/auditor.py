# coding=utf-8
from cache_registry.api.user import UserListView
from cache_registry.api.views import ApiView, DetailView, ListView
from cache_registry.models import Auditor


class AuditorListView(ListView):
    model = Auditor

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        data.update(
            {
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
        data.update(
            {
                "users": [UserListView.serialize(cp) for cp in obj.contact_persons],
            }
        )
        return data
