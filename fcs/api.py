import json
from datetime import datetime
from flask import Blueprint, Response
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address, Country,
    OldCompanyLink, db,
)

api = Blueprint('api', __name__)

api_manager = Manager()


@api_manager.command
def test():
    """ Return a list of all undertakings """
    import pprint

    undertakings = Undertaking.query.all()

    res = [u.as_dict() for u in undertakings]
    pprint.pprint(res)


class ApiView(MethodView):
    def dispatch_request(self, **kwargs):
        resp = super(ApiView, self).dispatch_request(**kwargs)

        if isinstance(resp, (dict, list, tuple)):
            return Response(json.dumps(resp), mimetype='application/json')

        return resp

    @classmethod
    def serialize(cls, obj):
        return obj.as_dict() if obj else None


class ListView(ApiView):
    def get_queryset(self):
        return self.model.query.all()

    def get(self):
        return [self.serialize(u) for u in self.get_queryset()]


class DetailView(ApiView):
    def get(self, pk):
        return self.serialize(self.model.query.get(pk))


class UndertakingList(ListView):
    model = Undertaking

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        data.update({
            'address': ApiView.serialize(obj.address),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
        })
        data.pop('address_id')
        data['address'].update({
            'country': ApiView.serialize(obj.address.country),
        })
        data['address'].pop('country_id')
        return data


class UndertakingDetail(DetailView):
    model = Undertaking

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        data.update({
            'address': ApiView.serialize(obj.address),
            'businessprofile': ApiView.serialize(obj.businessprofile),
            'represent': ApiView.serialize(obj.represent),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
        })
        data.pop('address_id')
        data.pop('businessprofile_id')
        data.pop('represent_id')
        data['address'].update({
            'country': ApiView.serialize(obj.address.country),
        })
        data['address'].pop('country_id')
        data['represent'].update({
            'address': ApiView.serialize(obj.represent.address),
        })
        data['represent'].pop('address_id')

        return data


class UserList(ListView):
    model = User


class CompaniesList(ListView):
    model = EuLegalRepresentativeCompany

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        data.update({
            'address': ApiView.serialize(obj.address),
        })
        data.pop('address_id')
        return data


class CandidateList(ApiView):
    def get(self):
        companies = Undertaking.query.filter_by(oldcompany=None)
        data = []
        for company in companies:
            if company.links:
                ls = [ApiView.serialize(l.oldcompany) for l in company.links]
                data.append(
                    {'undertaking': ApiView.serialize(company), 'links': ls}
                )
        return data


class CandidateVerify(ApiView):
    # TODO: we should use POST for this action
    def get(self, undertaking_id, oldcompany_id):
        link = (
            OldCompanyLink.query
            .filter_by(undertaking_id=undertaking_id,
                       oldcompany_id=oldcompany_id).first_or_404()
        )
        link.verified = True
        link.date_verified = datetime.now()
        link.undertaking.oldcompany = link.oldcompany
        db.session.commit()
        return ApiView.serialize(link)



api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('undertaking-list'))
api.add_url_rule('/undertaking/detail/<pk>',
                 view_func=UndertakingDetail.as_view('undertaking-detail'))
api.add_url_rule('/user/list',
                 view_func=UserList.as_view('user-list'))
api.add_url_rule('/company/list',
                 view_func=CompaniesList.as_view('company-list'))

api.add_url_rule('/candidate/list',
                 view_func=CandidateList.as_view('candidate-list'))
api.add_url_rule('/candidate/verify/<undertaking_id>/<oldcompany_id>/',
                 view_func=CandidateVerify.as_view('candidate-verify'))
