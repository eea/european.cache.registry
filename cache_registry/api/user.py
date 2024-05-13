from flask import current_app
from flask import request
from werkzeug.exceptions import abort

from cache_registry.api.views import ApiView, DetailView, ListView
from cache_registry.api.serializers import EuLegalRepresentativeCompanyDetail
from cache_registry.models import User


class UserListView(ListView):
    model = User


class UserCompaniesView(DetailView):
    model = User

    def get_object(self, pk, **kwargs):
        user = self.model.query.filter_by(username=pk).first()
        if not user:
            current_app.logger.warning(f"Unknown user: {pk}")
            abort(404)
        return user

    @classmethod
    def serialize(cls, obj, **kwargs):
        def _serialize(company):
            return {
                "company_id": company.external_id,
                "collection_id": company.oldcompany_account,
                "name": company.name,
                "domain": company.domain,
                "country": company.country_code,
                "country_history": [
                    country_hist.code for country_hist in company.country_history
                ],
                "representative_country": (
                    None
                    if not company.represent
                    else company.represent.address.country.code
                ),
                "represent_history": [
                    EuLegalRepresentativeCompanyDetail.serialize(representative_hist)
                    for representative_hist in company.represent_history
                ],
            }

        return [_serialize(c) for c in obj.verified_undertakings]


class UserCompaniesIncludeEcasView(ApiView):
    model = User

    def get_object(self, **kwargs):
        user = None
        checked_username = []
        import pdb

        pdb.set_trace()
        if "username" in request.args:
            username = request.args.get("username")
            checked_username.append(username)
            user = self.model.query.filter_by(username=username).first()
        if not user:
            if "ecas_id" in request.args:
                ecas_id = request.args.get("ecas_id")
                checked_username.append(ecas_id)
                user = self.model.query.filter_by(username=ecas_id).first()
        if not user:
            current_app.logger.warning(f"Unknown user: {''.join(checked_username)}")
            abort(404)
        return user

    @classmethod
    def serialize(cls, obj, **kwargs):
        def _serialize(company):
            return {
                "company_id": company.external_id,
                "collection_id": company.oldcompany_account,
                "name": company.name,
                "domain": company.domain,
                "country": company.country_code,
                "country_history": [
                    country_hist.code for country_hist in company.country_history
                ],
                "representative_country": (
                    None
                    if not company.represent
                    else company.represent.address.country.code
                ),
                "represent_history": [
                    EuLegalRepresentativeCompanyDetail.serialize(representative_hist)
                    for representative_hist in company.represent_history
                ],
            }

        return [_serialize(c) for c in obj.verified_undertakings]

    def get(self, **kwargs):
        return self.serialize(self.get_object(**kwargs))
