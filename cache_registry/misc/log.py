from datetime import datetime

from flask import Response

from sqlalchemy import desc

from cache_registry.models import OrganizationLog, MatchingLog, Undertaking
from cache_registry.api.views import ListView, ApiView


class DataSyncLogsView(ListView):
    model = OrganizationLog

    def get_queryset(self, **kwargs):
        return (self.model.query
                .filter_by(domain=kwargs['domain'])
                .order_by(desc(self.model.execution_time))
                .limit(100))


class MatchingLogsView(ListView):
    model = MatchingLog

    def get_queryset(self, **kwargs):
        return (self.model.query
                .filter_by(domain=kwargs['domain'])
                .order_by(desc(self.model.timestamp))
        )

    @classmethod
    def serialize(cls, obj, **kwargs):
        pop_id = kwargs.get('pop_id', True)
        data = ApiView.serialize(obj,
                                 pop_id=pop_id)
        u = Undertaking.query.filter_by(
            external_id=data['company_id']).first()
        if u:
            data['domain'] = u.domain
            data['country_code'] = u.country_code
        return data

    def get(self, **kwargs):
        return [self.serialize(u)
                for u in self.get_queryset(**kwargs)]

class CheckSyncLogsView(ApiView):

    def get(self, **kwargs):
        latest_log = OrganizationLog.query.filter_by(
            domain=kwargs['domain']).order_by(desc(OrganizationLog.execution_time)).first()
        time = datetime.now() - latest_log.execution_time
        if 3600 - time.seconds < 0:
            return Response("failed", status=500, mimetype="plain/text")
        return Response("success", status=200, mimetype="plain/text")
