# coding=utf-8
import datetime

from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import MultiYearLicence, Undertaking, CNQuantity


class MultiYearLicenceReturnsViewset(ListView):
    model = MultiYearLicence

    @classmethod
    def serialize(cls, obj, **kwargs):
        year = request.args.get("year")
        data = ApiView.serialize(obj)
        _strip_fields = ("undertaking_id",)
        for field in _strip_fields:
            data.pop(field)

        cn_quantities = CNQuantity.query.filter_by(multi_year_licence_id=obj.id)
        if year:
            cn_quantities = cn_quantities.filter_by(year=int(year))
        cn_quantities = cn_quantities.all()

        data.update(
            {
                "registration_id": obj.undertaking.registration_id,
                "external_id": obj.undertaking.external_id,
                "company_name": obj.undertaking.name,
                "cn_codes": [
                    {"code": cn.code, "description": cn.description}
                    for cn in obj.cn_codes
                ],
                "certex_information": [
                    {
                        "year": cn_quantity.year,
                        "combined_nomenclature_code": cn_quantity.combined_nomenclature.code,
                        "aggregated_reserved_ods_net_mass": str(
                            cn_quantity.aggregated_reserved_ods_net_mass
                        ),
                        "aggregated_consumed_ods_net_mass": str(
                            cn_quantity.aggregated_consumed_ods_net_mass
                        ),
                    }
                    for cn_quantity in cn_quantities
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
        external_id = request.args.get("external_id")
        year = request.args.get("year")
        try:
            external_id = int(external_id) if external_id else None
            year = int(year) if year else None
        except ValueError:
            return []

        multi_year_licences = MultiYearLicence.query

        if external_id:
            undertaking = Undertaking.query.filter_by(
                external_id=external_id, domain="ODS"
            ).first_or_404()
            multi_year_licences = MultiYearLicence.query.filter_by(
                undertaking_id=undertaking.id
            )
        if year:
            if year == 2025:
                multi_year_licences = multi_year_licences.filter(
                    MultiYearLicence.validity_end_date >= "2025-03-01",
                    MultiYearLicence.validity_start_date <= "2025-12-31",
                )
            else:
                start_date = datetime.date(year, 1, 1)
                end_date = datetime.date(year, 12, 31)
                multi_year_licences = multi_year_licences.filter(
                    MultiYearLicence.validity_end_date >= start_date,
                    MultiYearLicence.validity_start_date <= end_date,
                )
        return multi_year_licences
