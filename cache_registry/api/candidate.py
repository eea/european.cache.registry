from flask import abort
from flask import request

from cache_registry.api.views import ApiView

from cache_registry.match import (
    get_all_candidates,
    verify_none,
    verify_link,
    unverify_link,
    get_all_non_candidates,
    verify_manual)


class CandidateList(ApiView):

    def get(self, **kwargs):
        domain = kwargs.get('domain')
        candidates = get_all_candidates(domain)
        data = []
        for company, links in candidates:
            links_data = [{'name': l.oldcompany.name} for l in links]
            company_data = {
                'company_id': company.external_id,
                'name': company.name,
                'status': company.status,
                'country': company.address.country.name
            }
            data.append(
                {'undertaking': company_data, 'links': links_data}
            )
        return data


class NonCandidateList(ApiView):
    def get(self, domain):
        non_candidates = get_all_non_candidates(domain)
        return [ApiView.serialize(c) for c in non_candidates]


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

    def post(self, domain, undertaking_id, oldcompany_id):
        user = request.form['user']
        link = verify_link(undertaking_id, oldcompany_id,
                           user) or abort(404)
        return self.serialize(link, pop_id=False)


class CandidateVerifyNone(ApiView):

    @classmethod
    def serialize(cls, obj, pop_id=True):
        data = ApiView.serialize(obj, pop_id=pop_id)
        if data:
            data.pop('id')
        return data

    def post(self, domain, undertaking_id):
        user = request.form['user']
        link = verify_none(undertaking_id, domain, user) or abort(404)
        return self.serialize(link, pop_id=False)


class CandidateUnverify(ApiView):
    def post(self, domain, undertaking_id):
        user = request.form['user']
        link = unverify_link(undertaking_id=undertaking_id,
                             user=user,
                             domain=domain) or abort(404)
        return ApiView.serialize(link)


class CandidateVerifyManual(ApiView):
    @classmethod
    def serialize(cls, obj, pop_id=True):
        data = {
            'undertaking_id': obj.id,
            'oldcompany_account': obj.oldcompany_account,
            'verified': obj.oldcompany_verified,
        }
        return data

    def post(self, domain, undertaking_id, oldcompany_account):
        user = request.form['user']
        undertaking = verify_manual(undertaking_id, domain, oldcompany_account, user)
        return ApiView.serialize(undertaking)
