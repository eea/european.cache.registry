# coding=utf-8
import contextlib
import json
import sys
import StringIO

from sqlalchemy import desc
from flask import Blueprint, Response, abort, request, current_app
from flask.views import MethodView
from flask.ext.script import Manager
from fcs.models import (
    Undertaking, User, EuLegalRepresentativeCompany, Address,
    OrganizationLog, MatchingLog,
)
from fcs.match import (
    get_all_candidates, get_all_non_candidates, unverify_link,
    verify_none, str_matches,
)
from fcs.sync.commands import (
    fgases,
    fgases_debug_noneu,
    sync_collections_title
)

api = Blueprint('api', __name__)
api_manager = Manager()


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


class ApiView(MethodView):
    def dispatch_request(self, **kwargs):
        if not self.authenticate():
            resp = {
                'status': 'Unauthorized',
                'message': 'You need to be authenticated '
                           'in order to access this resource.',
            }
            status_code = 401
            return Response(json.dumps(resp, indent=2),
                            mimetype='application/json'), status_code

        resp = super(ApiView, self).dispatch_request(**kwargs)

        if isinstance(resp, (dict, list, tuple)):
            return Response(json.dumps(resp, indent=2),
                            mimetype='application/json')

        return resp

    def authenticate(self):
        token = current_app.config.get('API_TOKEN', '')
        authorization = request.headers.get('Authorization', '')
        if authorization == token:
            return True
        return False

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
        domain = request.args.get('domain', 'FGAS')
        return get_all_non_candidates(domain=domain)

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'businessprofile_id', 'address_id',
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


class UndertakingListSmall(ListView):
    model = Undertaking

    def get_queryset(self):
        domain = request.args.get('domain', 'FGAS')
        return get_all_non_candidates(domain=domain)

    @classmethod
    def serialize(cls, obj):
        if not obj:
            return None
        return {
            'company_id': obj.external_id,
            'name': obj.name,
            'domain': obj.domain,
            'vat': obj.vat,
            'date_created': obj.date_created.strftime('%d/%m/%Y'),
            'address': AddressDetail.serialize(obj.address),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
        }


class UndertakingListByVat(UndertakingList):
    def get_queryset(self, vat):
        domain = request.args.get('domain', 'FGAS')
        return get_all_non_candidates(vat=vat, domain=domain)

    @classmethod
    def serialize(cls, obj):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'businessprofile_id', 'address_id',
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
        'countrycode': 'country_code_orig',
        'vat': 'vat',
    }

    def get(self):
        qs = Undertaking.query
        if any([a for a in request.args if a.startswith('OR_')]):
            qs = Undertaking.query.join(EuLegalRepresentativeCompany)
        qs = qs.filter(Undertaking.oldcompany_verified == True)

        for k, v in request.args.iteritems():
            if k not in self.FILTERS:
                abort(400)
            if k == 'OR_vat':
                qs = qs.filter(EuLegalRepresentativeCompany.vatnumber == v)
            elif k != 'name' and k != 'OR_name':
                qs = qs.filter(getattr(Undertaking, self.FILTER_MAP[k]) == v)
        if 'name' in request.args:
            qs = [u for u in qs
                  if str_matches(u.name.lower(), request.args['name'].lower())]
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
        data = ApiView.serialize(obj)
        _strip_fields = (
            'date_updated', 'address_id', 'businessprofile_id',
            'represent_id',
        )
        for field in _strip_fields:
            data.pop(field)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'businessprofile': ApiView.serialize(obj.businessprofile),
            'representative': EuLegalRepresentativeCompanyDetail.serialize(
                obj.represent),
            'users': [UserList.serialize(cp) for cp in obj.contact_persons],
            'candidates': [],
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
        user = self.model.query.filter_by(username=pk).first()
        if not user:
            current_app.logger.warning('Unknown user: {}'.format(pk))
            abort(404)
        return user

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


class CandidateList(ListView):
    model = Undertaking

    def get_queryset(self):
        return get_all_candidates()

    @classmethod
    def serialize(cls, obj):
        data = {
            'company_id': obj.external_id,
            'name': obj.name,
            'status': obj.status,
            'country': obj.address.country.name
        }
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
            data['company_id'] = obj.undertaking.external_id
            data['collection_id'] = (
                obj.oldcompany and obj.oldcompany.external_id
            )
        return data

    def post(self, undertaking_id):
        user = request.form['user']
        undertaking = verify_none(undertaking_id, user) or abort(404)
        data = ApiView.serialize(undertaking)
        return {
            'verified': data['oldcompany_verified'],
            'company_id': data['company_id'],
        }


class CandidateUnverify(ApiView):
    def post(self, undertaking_id):
        user = request.form['user']
        link = unverify_link(undertaking_id, user) or abort(404)
        return ApiView.serialize(link)


class DataSyncLog(ListView):
    model = OrganizationLog

    def get_queryset(self, **kwargs):
        return (self.model.query
                .order_by(desc(self.model.execution_time))
                .limit(100))


class MatchingsLog(ListView):
    model = MatchingLog

    def get_queryset(self, **kwargs):
        return self.model.query.order_by(desc(self.model.timestamp))

    @classmethod
    def serialize(cls, obj, pop_id=True):
        data = ApiView.serialize(obj, pop_id)
        u = Undertaking.query.filter_by(external_id=data['company_id']).first()
        if u:
            data['domain'] = u.domain
            data['country_code'] = u.country_code
        return data


class MgmtCommand(ApiView):
    def get(self, **kwargs):
        kwargs = kwargs or request.args.to_dict()
        with stdout_redirect(StringIO.StringIO()) as output:
            try:
                success = self.command_func(**kwargs)
                message = ''
            except Exception as ex:
                success = False
                message = repr(ex)

        output.seek(0)
        message = output.read() + message

        return {'success': success, 'message': message}


class SyncFgases(MgmtCommand):
    command_func = staticmethod(fgases)


class SyncFgasesDebugNoneu(MgmtCommand):
    command_func = staticmethod(fgases_debug_noneu)


class SyncCollectionsTitle(MgmtCommand):
    command_func = staticmethod(sync_collections_title)


api.add_url_rule('/undertaking/list',
                 view_func=UndertakingList.as_view('company-list'))
api.add_url_rule('/undertaking/list-small',
                 view_func=UndertakingListSmall.as_view('company-list-small'))
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

api.add_url_rule('/candidate/verify/<undertaking_id>/',
                 view_func=CandidateVerify.as_view('candidate-verify'))
api.add_url_rule('/candidate/unverify/<undertaking_id>/',
                 view_func=CandidateUnverify.as_view('candidate-unverify'))

api.add_url_rule('/data_sync_log',
                 view_func=DataSyncLog.as_view('data-sync-log'))
api.add_url_rule('/matching_log',
                 view_func=MatchingsLog.as_view('matching-log'))

api.add_url_rule('/sync/collections_title',
                 view_func=SyncCollectionsTitle.as_view('sync-collections'))
api.add_url_rule('/sync/fgases',
                 view_func=SyncFgases.as_view('sync-fgases'))
api.add_url_rule('/sync/fgases_debug_noneu',
                 view_func=SyncFgasesDebugNoneu.as_view('sync-fgases-debug-noneu'))
