from sqlalchemy import desc

from fcs.models import OrganizationLog, MatchingLog, Undertaking
from fcs.api.views import ListView, ApiView


class DataSyncLogsView(ListView):
    model = OrganizationLog

    def get_queryset(self, **kwargs):
        return (self.model.query
                .order_by(desc(self.model.execution_time))
                .limit(100))


class MatchingLogsView(ListView):
    model = MatchingLog

    def get_queryset(self, **kwargs):
        return self.model.query.order_by(desc(self.model.timestamp))

    @classmethod
    def serialize(cls, obj, **kwargs):
        pop_id = kwargs.get('pop_id', True)
        data = ApiView.serialize(obj,
                                 pop_id=pop_id)
        u = Undertaking.query.fgases().filter_by(
            external_id=data['company_id']).first()
        if u:
            data['domain'] = u.domain
            data['country_code'] = u.country_code
        return data
