from cache_registry.api.views import (
    ApiView,
    DetailView
)

from cache_registry.models import (
    Address,
    EuLegalRepresentativeCompany
)


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