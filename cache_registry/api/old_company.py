import json

from cache_registry.api.views import ApiView, DetailView, ListView
from cache_registry.models import db, OldCompany


class OldCompanyDetail(DetailView):
    model = OldCompany

    @classmethod
    def serialize(cls, obj):
        rep = ApiView.serialize(obj)
        rep["country"] = obj.country
        return rep


class OldCompanyListByStatus(ListView):
    model = OldCompany

    def get_queryset(self, **kwargs):
        return self.model.query.filter_by(valid=self.valid).all()


class OldCompanyListValid(OldCompanyListByStatus):
    valid = True


class OldCompanyListInvalid(OldCompanyListByStatus):
    valid = False


class OldCompanySetStatus(DetailView):
    model = OldCompany

    def post(self, pk):
        company = self.model.query.filter_by(external_id=pk).first_or_404()
        company.valid = self.valid
        db.session.commit()
        return json.dumps(True)


class OldCompanySetValid(OldCompanySetStatus):
    valid = True


class OldCompanySetInvalid(OldCompanySetStatus):
    valid = False
