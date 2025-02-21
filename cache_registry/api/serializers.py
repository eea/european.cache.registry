from cache_registry.api.views import ApiView, DetailView
from cache_registry.models import (
    Address,
    Auditor,
    AuditorUndertaking,
    EuLegalRepresentativeCompany,
    User,
)


class AddressDetail(DetailView):
    model = Address

    @classmethod
    def serialize(cls, obj, **kwargs):
        addr = ApiView.serialize(obj)
        if not addr:
            return None
        addr["country"] = ApiView.serialize(obj.country)
        addr.pop("country_id")
        return addr


class EuLegalRepresentativeCompanyDetail(DetailView):
    model = EuLegalRepresentativeCompany

    @classmethod
    def serialize(cls, obj, **kwargs):
        rep = ApiView.serialize(obj)
        if not rep:
            return None
        rep["address"] = AddressDetail.serialize(obj.address)
        rep.pop("address_id")
        return rep


class UserDetail(DetailView):
    model = User


class AuditorDetail(DetailView):
    model = Auditor

    @classmethod
    def serialize(cls, obj, **kwargs):
        rep = ApiView.serialize(obj)
        _strip_fields = ("address_id",)
        for field in _strip_fields:
            rep.pop(field)
        rep.update(
            {
                "ms_accreditation_issuing_countries": [
                    country.code for country in obj.ms_accreditation_issuing_countries
                ],
                "address": AddressDetail.serialize(obj.address),
                "users": [UserDetail.serialize(cp) for cp in obj.contact_persons],
            }
        )
        return rep


class AuditorUndertakingDetail(DetailView):
    model = AuditorUndertaking

    @classmethod
    def serialize(cls, obj, **kwargs):
        rep = ApiView.serialize(obj)
        _strip_fields = ("undertaking_id", "auditor_id", "user_id")
        for field in _strip_fields:
            rep.pop(field)
        rep["auditor"] = {
            "auditor_uid": obj.auditor.auditor_uid,
            "name": obj.auditor.name,
        }
        rep["undertaking"] = {
            "company_id": obj.undertaking.external_id,
            "domain": obj.undertaking.domain,
            "name": obj.undertaking.name,
        }
        rep["user"] = UserDetail.serialize(obj.user)
        return rep
