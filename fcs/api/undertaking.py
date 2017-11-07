# coding=utf-8
import json

from flask import abort, request

from fcs.api.views import DetailView, ListView, ApiView
from fcs.api.old_company import OldCompanyDetail
from fcs.api.user import UserListView
from fcs.models import Undertaking, EuLegalRepresentativeCompany, Address, db
from fcs.match import get_all_non_candidates, str_matches, get_candidates


class AddressDetail(DetailView):
    model = Address

    @classmethod
    def serialize(cls, obj, **kwargs):
        addr = ApiView.serialize(obj)
        if not addr:
            return None
        addr['country'] = ApiView.serialize(obj.country)
        addr.pop('country_id')
        return addr


class EuLegalRepresentativeCompanyDetail(DetailView):
    model = EuLegalRepresentativeCompany

    @classmethod
    def serialize(cls, obj, **kwargs):
        rep = ApiView.serialize(obj)
        if not rep:
            return None
        rep['address'] = AddressDetail.serialize(obj.address)
        rep.pop('address_id')
        return rep


class UndertakingListView(ListView):
    model = Undertaking

    def get_queryset(self, domain, **kwargs):
        return get_all_non_candidates(domain=domain)

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'address_id', 'represent_id',
            'oldcompany_id'
        )
        for field in _strip_fields:
            data.pop(field)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'users': [UserListView.serialize(cp) for cp in obj.contact_persons],
            'types': ",".join([type.type for type in obj.types]),
            'representative': EuLegalRepresentativeCompanyDetail.serialize(
                obj.represent),
            'businessprofile': ",".join(
                [businessprofiles.highleveluses for
                 businessprofiles in obj.businessprofiles]
            )
        })
        data['company_id'] = obj.external_id
        data['collection_id'] = obj.oldcompany_account
        return data


class UndertakingListSmallView(ListView):
    model = Undertaking

    def get_queryset(self, domain):
        return get_all_non_candidates(domain=domain)

    @classmethod
    def serialize(cls, obj, **kwargs):
        if not obj:
            return None
        return {
            'company_id': obj.external_id,
            'name': obj.name,
            'domain': obj.domain,
            'vat': obj.vat,
            'date_created': obj.date_created.strftime('%d/%m/%Y'),
            'address': AddressDetail.serialize(obj.address),
            'users': [UserListView.serialize(cp) for cp in obj.contact_persons],
        }


class UndertakingListByVatView(UndertakingListView):
    def get_queryset(self, domain, **kwargs):
        vat = kwargs.get('vat', '')
        return get_all_non_candidates(vat=vat,
                                      domain=domain)

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = (
            'address_id', 'oldcompany_id', 'represent_id',
            'phone', 'country_code', 'date_created', 'oldcompany_account',
            'oldcompany_extid', 'domain', 'website', 'status',
            'undertaking_type', 'date_updated', 'oldcompany_verified', 'vat'
        )
        for field in _strip_fields:
            data.pop(field)
        data['company_id'] = obj.external_id
        return data


class UndertakingFilterCountView(ListView):
    FILTERS = ('id', 'vat', 'name', 'countrycode', 'OR_vat', 'OR_name')
    FILTER_MAP = {
        'id': 'external_id',
        'countrycode': 'country_code_orig',
        'vat': 'vat',
    }

    def get_queryset(self, domain, **kwargs):
        qs = Undertaking.query.filter_by(domain=domain)
        if any([a for a in request.args if a.startswith('OR_')]):
            qs = qs.join(EuLegalRepresentativeCompany)
        qs = qs.filter(Undertaking.oldcompany_verified == True)

        for k, v in request.args.iteritems():
            if k not in self.FILTERS:
                abort(400)
            if k == 'OR_vat':
                qs = qs.filter(EuLegalRepresentativeCompany.vatnumber == v)
            elif k != 'name' and k != 'OR_name':
                qs = qs.filter(getattr(Undertaking, self.FILTER_MAP[k]) == v)
        return qs

    def get(self, **kwargs):
        qs = self.get_queryset(**kwargs)
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


class UndertakingListAllView(UndertakingListView):
    def get_queryset(self, domain, **kwargs):
        return self.model.query.filter_by(domain=domain)


class UndertakingDetailView(DetailView):
    model = Undertaking

    def get_object(self, pk, **kwargs):
        domain = kwargs.get('domain')
        return self.model.query.filter_by(domain=domain,
                                          external_id=pk).first_or_404()

    @classmethod
    def serialize(cls, obj, **kwargs):
        candidates = get_candidates(obj.external_id, obj.domain)
        data = ApiView.serialize(obj)
        _strip_fields = (
            'date_updated', 'address_id',
            'represent_id',
        )
        for field in _strip_fields:
            data.pop(field)
        data.update({
            'address': AddressDetail.serialize(obj.address),
            'businessprofile': ",".join(
                [businessprofile.highleveluses for
                 businessprofile in obj.businessprofiles]
            ),
            'representative': EuLegalRepresentativeCompanyDetail.serialize(
                obj.represent),
            'users': [UserListView.serialize(cp) for cp in obj.contact_persons],
            'candidates': [OldCompanyDetail.serialize(c.oldcompany) for c in
                           candidates],
            'types': ",".join([type.type for type in obj.types])
        })
        data['company_id'] = obj.external_id
        data['collection_id'] = obj.oldcompany_account
        return data


class UndertakingStatusUpdate(ApiView):
    model = Undertaking

    def post(self, domain, pk):
        status = request.form['status']
        if status:
            company = self.model.query.filter_by(
                domain=domain,
                external_id=pk).first_or_404()
            company.status = status
            db.session.commit()
            return json.dumps(True)
        return json.dumps(False)
