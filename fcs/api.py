import json
from flask import Blueprint, Response
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address, Country,
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
        return obj.as_dict()


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
        data = obj.as_dict()
        data.update({
            'address': obj.address.as_dict(),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
        })
        data.pop('address_id')
        return data


class UndertakingDetail(DetailView):
    model = Undertaking

    @classmethod
    def serialize(cls, obj):
        data = obj.as_dict()
        data.update({
            'address': obj.address.as_dict(),
            'businessprofile': obj.businessprofile.as_dict(),
            'represent': obj.represent.as_dict(),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
        })
        data.pop('address_id')
        data.pop('businessprofile_id')
        data.pop('represent_id')
        return data


class UserList(ListView):
    model = User

    @classmethod
    def serialize(cls, obj):
        return obj.as_dict()


class CompaniesList(ListView):
    model = EuLegalRepresentativeCompany


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('undertaking-list'))
api.add_url_rule('/undertaking/detail/<pk>',
                 view_func=UndertakingDetail.as_view('undertaking-detail'))
api.add_url_rule('/user/list',
                 view_func=UserList.as_view('user-list'))
api.add_url_rule('/company/list',
                 view_func=CompaniesList.as_view('companies-list'))
