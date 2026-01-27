# coding=utf-8
from functools import reduce
import json

from flask import current_app
from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import MultiYearLicence, Undertaking


class MultiYearLicenceReturnsViewset(ListView):
    model = MultiYearLicence

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("undertaking_id",)
        for field in _strip_fields:
            data.pop(field)
        data.update(
            {
                "external_id": obj.undertaking.external_id,
                "company_name": obj.undertaking.name,
                "cn_codes": [
                    {"code": cn.code, "description": cn.description}
                    for cn in obj.cn_codes
                ],
                "substances": [
                    {
                        "name": substance.name,
                        "chemical_name": substance.chemical_name,
                    }
                    for substance in obj.substances
                ],
                "detailed_uses": [
                    {
                        "short_code": link.detailed_use.short_code,
                        "code": link.detailed_use.code,
                        "valid_until": link.valid_until,
                    }
                    for link in obj.detailed_uses_link
                ],
            }
        )
        return data

    def get_queryset(self, **kwargs):
        data = request.args.get("data")
        external_id = request.args.get("external_id")
        if data == "multi_year_licences":
            multi_year_licences = MultiYearLicence.query.all()
            if external_id:
                undertaking = Undertaking.query.filter_by(
                    external_id=external_id, domain="ODS"
                ).first_or_404()
                multi_year_licences = MultiYearLicence.query.filter_by(
                    undertaking_id=undertaking.id
                ).all()
            return multi_year_licences
        return []
