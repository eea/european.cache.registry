# coding=utf-8
import json
from openpyxl import Workbook

from flask import Blueprint, Response, abort, request
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address, OldCompany,
    OrganizationLog, MatchingLog,
)
from fcs.match import (
    get_all_candidates, get_all_non_candidates, verify_link, unverify_link,
    get_candidates, verify_none,
)
from openpyxl.writer.excel import save_virtual_workbook

api = Blueprint('api', __name__)
api_manager = Manager()


MIMETYPE = 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'


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
        })
        data['company_id'] = obj.external_id
        data['collection_id'] = obj.oldcompany_account
        return data


class UndertakingListByVat(ListView):
    model = Undertaking

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


class UndertakingListAll(UndertakingList):

    def get_queryset(self):
        return self.model.query.all()


class UndertakingListExport(UndertakingList):

    columns = [
        'company_id', 'name', 'domain', 'status', 'undertaking_type', 'website',
        'date_updated', 'phone', 'oldcompany_extid', 'address_city',
        'address_country_code', 'address_country_name', 'address_country_type',
        'address_zipcode', 'address_number', 'address_street', 'country_code',
        'vat', 'users', 'users',  'types', 'collection_id', 'date_created',
        'oldcompany_account', 'oldcompany_verified', 'representative_name',
        'representative_contact_first_name', 'representative_contact_last_name',
        'representative_vatnumber', 'representative_contact_email',
        'representative_address_zipcode', 'representative_address_number',
        'representative_address_street', 'representative_address_city',
        'representative_address_country_code',
        'representative_address_country_type',
        'representative_address_country_name'
    ]

    def parse_column(self, qs, column):
        def _parse_address(qs, column):
            for sub_column in column.split('_'):
                qs = qs[sub_column]
            return qs

        if column.startswith('address'):
            return _parse_address(qs, column)
        elif column.startswith('representative'):
            repr_info = column.split('_', 1)[1]
            qs = qs['representative']
            if not qs:
                return None
            if repr_info.startswith('address'):
                return _parse_address(qs, repr_info)
            return qs[repr_info]
        return qs[column]

    def get(self, **kwargs):
        queryset = super(UndertakingListExport, self).get(**kwargs)

        wb = Workbook()
        ws = wb.active
        ws.title = 'Companies List'
        ws.append(self.columns)
        for qs in queryset:
            qs['users'] = ', '.join([user['username'] for user in qs['users']])
            values = [self.parse_column(qs, column) for column in self.columns]
            ws.append(values)
        response = Response(save_virtual_workbook(wb), mimetype=MIMETYPE)
        response.headers.add('Content-Disposition',
                             'attachment; filename=companies_list.xlsx')
        return response


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
            'businessprofile_id', 'represent_id', 'types',
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
        data['@type'] = data.pop('undertaking_type')
        return data


class UserList(ListView):
    model = User


class UserCompanies(DetailView):
    model = User

    def get_object(self, pk):
        if '@' in pk:
            key = 'email'
        else:
            key = 'username'
        return self.model.query.filter_by(**{key: pk}).first_or_404()

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
        if not rep:
            return None
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
            data[
                'collection_id'] = obj.oldcompany and obj.oldcompany.external_id
        return data

    def post(self, undertaking_id, oldcompany_id):
        user = request.form['user']
        link = verify_link(undertaking_id, oldcompany_id, user) or abort(404)
        return self.serialize(link, pop_id=False)


class CandidateVerifyNone(CandidateVerify):
    def post(self, undertaking_id):
        user = request.form['user']
        link = verify_none(undertaking_id, user) or abort(404)
        return ApiView.serialize(link)


class CandidateUnverify(ApiView):
    def post(self, undertaking_id):
        user = request.form['user']
        link = unverify_link(undertaking_id, user) or abort(404)
        return ApiView.serialize(link)


class DataSyncLog(ListView):
    model = OrganizationLog


class MatchingsLog(ListView):
    model = MatchingLog


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('company-list'))
api.add_url_rule('/undertaking/list/all',
                 view_func=UndertakingListAll.as_view('company-list-all'))
api.add_url_rule('/undertaking/list_by_vat/<vat>',
                 view_func=UndertakingListByVat.as_view('company-list-by-vat'))
api.add_url_rule('/undertaking/<pk>/details',
                 view_func=UndertakingDetail.as_view('company-detail'))
api.add_url_rule('/undertaking/list/export',
                 view_func=UndertakingListExport.as_view('company-list-export'))

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

api.add_url_rule('/data_sync_log',
                 view_func=DataSyncLog.as_view('data-sync-log'))
api.add_url_rule('/matching_log',
                 view_func=MatchingsLog.as_view('matching-log'))
