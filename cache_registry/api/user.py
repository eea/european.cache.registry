from flask import current_app
from werkzeug.exceptions import abort

from cache_registry.api.views import ListView, DetailView
from cache_registry.models import User


class UserListView(ListView):
    model = User


class UserCompaniesView(DetailView):
    model = User

    def get_object(self, pk, **kwargs):
        if '@' in pk:
            abort(400)
        user = self.model.query.filter_by(username=pk).first()
        if not user:
            current_app.logger.warning('Unknown user: {}'.format(pk))
            abort(404)
        return user

    @classmethod
    def serialize(cls, obj, **kwargs):
        def _serialize(company):
            return {
                'company_id': company.external_id,
                'collection_id': company.oldcompany_account,
                'name': company.name,
                'domain': company.domain,
                'country': company.country_code,
            }

        return [_serialize(c) for c in obj.verified_undertakings]
