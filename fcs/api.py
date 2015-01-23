# coding=utf-8
import json

from sqlalchemy import desc
from flask import Blueprint, Response, abort, request, current_app
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address, OldCompany,
    OrganizationLog, MatchingLog, db,
)
from fcs.match import (
    get_all_candidates, get_all_non_candidates, verify_link, unverify_link,
    get_candidates, verify_none,
    str_matches)

api = Blueprint('api', __name__)
api_manager = Manager()


class ApiView(MethodView):
    def dispatch_request(self, **kwargs):
        resp = super(ApiView, self).dispatch_request(**kwargs)

        if isinstance(resp, (dict, list, tuple)):
            return Response(json.dumps(resp, indent=2),
                            mimetype='application/json')

        return resp

    @classmethod
    def serialize(cls, obj, pop_id=True):
        if not obj:
            return None
        data = obj.as_dict()
        if pop_id:
            data.pop('id')
        return data


class ListView(ApiView):
    def get_queryset(self, **kwargs):
        return self.model.query.all()

    def get(self, **kwargs):
        return [self.serialize(u) for u in self.get_queryset(**kwargs)]


class DetailView(ApiView):
    def get_object(self, pk):
        return self.model.query.get_or_404(pk)

    def get(self, pk):
        return self.serialize(self.get_object(pk))


class UndertakingList(ListView):
    model = Undertaking

    def get_queryset(self):
        return get_all_non_candidates()

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'businessprofile_id', 'address_id', 'oldcompany_id',
            'represent_id',
        )
        for field in _strip_fields:
            data.pop(field)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
            'representative': EuLegalRepresentativeCompanyDetail.serialize(
                obj.represent),
            'businessprofile': ApiView.serialize(obj.businessprofile)
        })
        data['company_id'] = obj.external_id
        data['collection_id'] = obj.oldcompany_account
        return data


class UndertakingListByVat(UndertakingList):
    def get_queryset(self, vat):
        return get_all_non_candidates(vat=vat)

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'businessprofile_id', 'address_id', 'oldcompany_id',
            'represent_id', 'phone', 'country_code', 'date_created',
            'oldcompany_account', 'types', 'oldcompany_extid', 'domain',
            'website', 'status', 'undertaking_type', 'date_updated',
            'oldcompany_verified', 'vat'
        )
        for field in _strip_fields:
            data.pop(field)
        data['company_id'] = obj.external_id
        return data


class UndertakingFilterCount(ApiView):
    FILTERS = ('id', 'vat', 'name', 'countrycode', 'OR_vat', 'OR_name')
    FILTER_MAP = {
        'id': 'external_id',
        'countrycode': 'country_code',
        'vat': 'vat',
    }

    def get(self):
        qs = Undertaking.query
        if any([a for a in request.args if a.startswith('OR_')]):
            qs = Undertaking.query.join(EuLegalRepresentativeCompany)
        qs = qs.filter(Undertaking.oldcompany_verified==True)

        for k, v in request.args.iteritems():
            if k not in self.FILTERS:
                abort(400)
            if k == 'OR_vat':
                qs = qs.filter(EuLegalRepresentativeCompany.vatnumber == v)
            elif k != 'name' and k != 'OR_name':
                qs = qs.filter(getattr(Undertaking, self.FILTER_MAP[k]) == v)
        if 'name' in request.args:
            qs = [u for u in qs if str_matches(u.name, request.args['name'])]
            count = len(qs)
        elif 'OR_name' in request.args:
            qs = [u for u in qs if
                  str_matches(u.represent.name, request.args['OR_name'])]
            count = len(qs)
        else:
            count = qs.count()
        return {'exists': count > 0, 'count': count}


class UndertakingListAll(UndertakingList):
    def get_queryset(self):
        return self.model.query.all()


class UndertakingDetail(DetailView):
    model = Undertaking

    def get_object(self, pk):
        return self.model.query.filter_by(external_id=pk).first_or_404()

    @classmethod
    def serialize(cls, obj):
        candidates = get_candidates(obj.external_id)
        data = ApiView.serialize(obj)
        _strip_fields = (
            'country_code', 'date_created', 'date_updated', 'address_id',
            'businessprofile_id', 'represent_id',
        )
        for field in _strip_fields:
            data.pop(field)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'businessprofile': ApiView.serialize(obj.businessprofile),
            'representative': EuLegalRepresentativeCompanyDetail.serialize(
                obj.represent),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
            'candidates': [OldCompanyDetail.serialize(c.oldcompany) for c in
                           candidates],
        })
        data['company_id'] = obj.external_id
        data['collection_id'] = obj.oldcompany_account
        return data


class UserList(ListView):
    model = User


class UserCompanies(DetailView):
    model = User

    def get_object(self, pk):
        if '@' in pk:
            abort(400)
        return self.model.query.filter_by(username=pk).first_or_404()

    @classmethod
    def serialize(cls, obj):
        def _serialize(company):
            return {
                'company_id': company.external_id,
                'collection_id': company.oldcompany_account,
                'name': company.name,
                'domain': company.domain,
                'country': company.country_code,
            }

        return [_serialize(c) for c in obj.verified_undertakings]


class AddressDetail(DetailView):
    model = Address

    @classmethod
    def serialize(cls, obj):
        addr = ApiView.serialize(obj)
        if not addr:
            return None
        addr['country'] = ApiView.serialize(obj.country)
        addr.pop('country_id')
        return addr


class EuLegalRepresentativeCompanyDetail(DetailView):
    model = EuLegalRepresentativeCompany

    @classmethod
    def serialize(cls, obj):
        rep = ApiView.serialize(obj)
        if not rep:
            return None
        rep['address'] = AddressDetail.serialize(obj.address)
        rep.pop('address_id')
        return rep


class OldCompanyDetail(DetailView):
    model = OldCompany

    @classmethod
    def serialize(cls, obj):
        rep = ApiView.serialize(obj)
        rep['country'] = obj.country
        return rep


class CandidateList(ApiView):
    def get(self):
        candidates = get_all_candidates()
        data = []
        for company, links in candidates:
            ls = [ApiView.serialize(l.oldcompany) for l in links]
            company_data = ApiView.serialize(company)
            company_data['company_id'] = company.external_id
            data.append(
                {'undertaking': company_data, 'links': ls}
            )
        return data


class NonCandidateList(ApiView):
    def get(self):
        noncandidates = get_all_non_candidates()
        return [ApiView.serialize(c) for c in noncandidates]


class CandidateVerify(ApiView):
    @classmethod
    def serialize(cls, obj, pop_id=True):
        data = ApiView.serialize(obj, pop_id=pop_id)
        if data:
            data.pop('undertaking_id')
            data.pop('oldcompany_id')
            data['company_id'] = obj.undertaking.external_id
            data['collection_id'] = (
                obj.oldcompany and obj.oldcompany.external_id
            )
        return data

    def post(self, undertaking_id, oldcompany_id):
        user = request.form['user']
        link = verify_link(undertaking_id, oldcompany_id, user) or abort(404)
        return self.serialize(link, pop_id=False)


class CandidateVerifyNone(CandidateVerify):
    def post(self, undertaking_id):
        user = request.form['user']
        undertaking = verify_none(undertaking_id, user) or abort(404)
        data = ApiView.serialize(undertaking)
        return {
            'verified': data['oldcompany_verified'],
            'company_id': data['company_id'],
        }


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


class CandidateUnverify(ApiView):
    def post(self, undertaking_id):
        user = request.form['user']
        link = unverify_link(undertaking_id, user) or abort(404)
        return ApiView.serialize(link)


class DataSyncLog(ListView):
    model = OrganizationLog

    def get_queryset(self, **kwargs):
        return self.model.query.order_by(desc(self.model.execution_time))


class MatchingsLog(ListView):
    model = MatchingLog

    def get_queryset(self, **kwargs):
        return self.model.query.order_by(desc(self.model.timestamp))


class OrgMatching(MethodView):
    def get(self, **kwargs):
        auto_config = current_app.config.get('AUTO_VERIFY_NEW_COMPANIES',
                                             False)
        return json.dumps(auto_config)


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('company-list'))
api.add_url_rule('/undertaking/list/all',
                 view_func=UndertakingListAll.as_view('company-list-all'))
api.add_url_rule('/undertaking/list_by_vat/<vat>',
                 view_func=UndertakingListByVat.as_view('company-list-by-vat'))
api.add_url_rule('/undertaking/filter/',
                 view_func=UndertakingFilterCount.as_view('company-filter'))
api.add_url_rule('/undertaking/<pk>/details',
                 view_func=UndertakingDetail.as_view('company-detail'))

api.add_url_rule('/user/list',
                 view_func=UserList.as_view('user-list'))
api.add_url_rule('/user/<pk>/companies',
                 view_func=UserCompanies.as_view('user-companies'))

api.add_url_rule('/candidate/list',
                 view_func=CandidateList.as_view('candidate-list'))

api.add_url_rule('/candidate/list/verified',
                 view_func=NonCandidateList.as_view('noncandidate-list'))

api.add_url_rule('/candidate/verify/<undertaking_id>/<oldcompany_id>/',
                 view_func=CandidateVerify.as_view('candidate-verify'))
api.add_url_rule('/candidate/verify-none/<undertaking_id>/',
                 view_func=CandidateVerifyNone.as_view(
                     'candidate-verify-none'))
api.add_url_rule('/candidate/unverify/<undertaking_id>/',
                 view_func=CandidateUnverify.as_view('candidate-unverify'))

api.add_url_rule('/oldcompanies/list/valid/',
                 view_func=OldCompanyListValid.as_view(
                     'oldcompany-list-valid'))
api.add_url_rule('/oldcompanies/list/invalid/',
                 view_func=OldCompanyListInvalid.as_view(
                     'oldcompany-list-invalid'))
api.add_url_rule('/oldcompanies/<pk>/valid/',
                 view_func=OldCompanySetValid.as_view(
                     'oldcompany-set-valid'))
api.add_url_rule('/oldcompanies/<pk>/invalid/',
                 view_func=OldCompanySetInvalid.as_view(
                     'oldcompany-set-invalid'))

api.add_url_rule('/data_sync_log',
                 view_func=DataSyncLog.as_view('data-sync-log'))
api.add_url_rule('/matching_log',
                 view_func=MatchingsLog.as_view('matching-log'))
api.add_url_rule('/organisation_matching',
                 view_func=OrgMatching.as_view('organisation-matching'))
