from flask import abort
from flask import request

from fcs.api.views import ListView, ApiView

from fcs.match import (
    get_all_candidates,
    verify_none,
    unverify_link,
    get_all_non_candidates
)
from fcs.models import Undertaking


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

    def post(self, domain, undertaking_id):
        user = request.form['user']
        link = verify_link(undertaking_id,
                           oldcompany_id, user) or abort(404)
        undertaking = verify_none(undertaking_id=undertaking_id,
                                  user=user,
                                  domain=domain) or abort(404)
        data = ApiView.serialize(undertaking)
        return {
            'verified': data['oldcompany_verified'],
            'company_id': data['company_id'],
        }


class CandidateVerifyNone(CandidateVerify):
    def post(self, undertaking_id):
        user = request.form['user']
        undertaking = verify_none(undertaking_id, user) or abort(404)
        data = ApiView.serialize(undertaking)
        return {
            'verified': data['oldcompany_verified'],
            'company_id': data['company_id'],
        }


class CandidateUnverify(ApiView):
    def post(self, domain, undertaking_id):
        user = request.form['user']
        link = unverify_link(undertaking_id=undertaking_id,
                             user=user,
                             domain=domain) or abort(404)
        return ApiView.serialize(link)
