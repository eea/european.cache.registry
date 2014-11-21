import json

from flask import Blueprint, Response, abort
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address, Country,
    OldCompanyLink, db, OldCompany
)
from fcs.match import (
    get_all_candidates, get_all_non_candidates, verify_link, unverify_link,
    get_candidates,
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
            return Response(json.dumps(resp, indent=2), mimetype='application/json')

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
    def get_object(self, pk):
        return self.model.query.get_or_404(pk)

    def get(self, pk):
        return self.serialize(self.get_object(pk))


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

    def get_object(self, pk):
        return self.model.query.filter_by(external_id=pk).first()

    @classmethod
    def serialize(cls, obj):
        candidates = get_candidates(obj.external_id)
        data = ApiView.serialize(obj)
        data.update({
            'address': ApiView.serialize(obj.address),
            'businessprofile': ApiView.serialize(obj.businessprofile),
            'represent': ApiView.serialize(obj.represent),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
            'candidates': [ApiView.serialize(c.oldcompany) for c in candidates],
        })
        data.pop('address_id')
        data.pop('businessprofile_id')
        data.pop('represent_id')
        if data['address']:
            data['address'].update({
                'country': ApiView.serialize(obj.address.country),
            })
            data['address'].pop('country_id')
        if data['represent']:
            data['represent'].update({
                'address': ApiView.serialize(obj.represent.address),
            })
            data['represent'].pop('address_id')

        return data


class UndertakingFullDetail(DetailView):
    model = Undertaking

    def get_object(self, pk):
        return self.model.query.filter_by(external_id=pk).first()

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
            'euLegalRepresentativeCompany':
            EuLegalRepresentativeCompanyDetail.serialize(obj.represent),
        })
        data.pop('country_code')
        data.pop('date_created')
        data.pop('date_updated')
        data.pop('address_id')
        data.pop('businessprofile_id')
        data.pop('represent_id')
        data.pop('types')
        data['Former_Company_no_2007-2010'] = data.pop('oldcompany_id')
        data['@type'] = data.pop('undertaking_type')
        data['id'] = data.pop('external_id')
        data['contactPersons'] = data.pop('users')
        for cp in data['contactPersons']:
            cp['userName'] = cp.pop('username')
            cp['firstName'] = cp.pop('first_name')
            cp['lastName'] = cp.pop('last_name')
            cp['emailAddress'] = cp.pop('email')
            cp.pop('id')
        data['address']['country'].pop('id')
        data['address'].pop('id')
        if obj.represent:
            r = 'euLegalRepresentativeCompany'
            data[r].pop('id')
            data[r]['address'].pop('id')
            data[r]['address']['country'].pop('id')

        return data


class UserList(ListView):
    model = User


class UserDetail(DetailView):
    model = User

    def get_object(self, pk):
        return self.model.query.filter_by(username=pk).first_or_404()

    @classmethod
    def serialize(cls, obj):
        def _serialize(company):
            old_company = company.oldcompany
            collection_id = old_company.account if old_company else None
            return {
                'company_id': company.external_id, 'name': company.name,
                'domain': company.domain, 'country': company.country_code,
                'id': company.id, 'account': company.old_account,
                'collection_id': collection_id,
            }

        return [_serialize(c) for c in obj.undertakings]


class CountryDetail(DetailView):
    model = Country

    @classmethod
    def serialize(cls, obj):
        return ApiView.serialize(obj)


class AddressDetail(DetailView):
    model = Address

    @classmethod
    def serialize(cls, obj):
        addr = ApiView.serialize(obj)
        if not addr:
            return None
        addr['country'] = ApiView.serialize(obj.country)
        addr['zipCode'] = addr.pop('zipcode')
        addr.pop('country_id')
        return addr


class EuLegalRepresentativeCompanyDetail(DetailView):
    model = EuLegalRepresentativeCompany

    @classmethod
    def serialize(cls, obj):
        rep = ApiView.serialize(obj)
        if not rep:
            return None
        rep.update({
            'address': AddressDetail.serialize(obj.address),
        })
        rep.pop('address_id')
        rep['vatNumber'] = rep.pop('vatnumber')
        rep['contactPersonFirstName'] = rep.pop('contact_first_name')
        rep['contactPersonLastName'] = rep.pop('contact_last_name')
        rep['contactPersonEmailAddress'] = rep.pop('contact_email')
        return rep


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
        candidates = get_all_candidates()
        data = []
        for company, links in candidates:
            ls = [ApiView.serialize(l.oldcompany) for l in links]
            data.append(
                {'undertaking': ApiView.serialize(company), 'links': ls}
            )
        return data


class NonCandidateList(ApiView):
    def get(self):
        noncandidates = get_all_non_candidates()
        return [ApiView.serialize(c) for c in noncandidates]


class CandidateVerify(ApiView):
    # TODO: we should use POST for this action
    def get(self, undertaking_id, oldcompany_id):
        link = verify_link(undertaking_id, oldcompany_id) or abort(404)
        return ApiView.serialize(link)


class CandidateUnverify(ApiView):
    # TODO: we should use POST for this action
    def get(self, undertaking_id, oldcompany_id):
        link = unverify_link(undertaking_id, oldcompany_id) or abort(404)
        return ApiView.serialize(link)


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('undertaking-list'))
api.add_url_rule('/undertaking/detail/<pk>',
                 view_func=UndertakingDetail.as_view('undertaking-detail'))
api.add_url_rule('/undertaking/full-detail/<pk>',
                 view_func=UndertakingFullDetail
                 .as_view('undertaking-full-detail'))

api.add_url_rule('/user/list',
                 view_func=UserList.as_view('user-list'))
api.add_url_rule('/user/detail/<pk>',
                 view_func=UserDetail.as_view('user-detail'))

api.add_url_rule('/company/list',
                 view_func=CompaniesList.as_view('company-list'))

api.add_url_rule('/candidate/list',
                 view_func=CandidateList.as_view('candidate-list'))

api.add_url_rule('/noncandidate/list',
                 view_func=NonCandidateList.as_view('noncandidate-list'))

api.add_url_rule('/candidate/verify/<undertaking_id>/<oldcompany_id>/',
                 view_func=CandidateVerify.as_view('candidate-verify'))
api.add_url_rule('/candidate/unverify/<undertaking_id>/<oldcompany_id>/',
                 view_func=CandidateUnverify.as_view('candidate-unverify'))
