# coding=utf-8
import datetime

from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import MultiYearLicence, Undertaking, CNQuantity


class MultiYearLicenceSerializerMixin:
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
                        "customs_procedure": cn_quantity.customs_procedure,
                        "aggregated_reserved_ods_net_mass": str(
                            cn_quantity.aggregated_reserved_ods_net_mass
                        ),
                        "aggregated_consumed_ods_net_mass": str(
                            cn_quantity.aggregated_consumed_ods_net_mass
                        ),
                    }
                    for cn_quantity in cn_quantities
                ],
                "aggregated_data": [
                    {
                        "year": agg.year,
                        "organization_country_name": agg.organization_country_name,
                        "substance": agg.substance,
                        "lic_use_kind": agg.lic_use_kind,
                        "lic_use_desc": agg.lic_use_desc,
                        "lic_type": agg.lic_type,
                        "aggregated_reserved_ods_net_mass": str(
                            agg.aggregated_reserved_ods_net_mass
                        ),
                        "aggregated_consumed_ods_net_mass": str(
                            agg.aggregated_consumed_ods_net_mass
                        ),
                        "has_certex_data": agg.has_certex_data,
                        "created_from_certex": agg.created_from_certex,
                    }
                    for agg in obj.aggregated_info
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
                        "short_code": detailed_use.short_code,
                        "code": detailed_use.code,
                    }
                    for detailed_use in obj.detailed_uses
                ],
            }
        )
        return data

class MultiYearLicenceReturnsViewset(MultiYearLicenceSerializerMixin, ListView):
    model = MultiYearLicence

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
                undertaking_id=undertaking.id, status="VALID"
            )
        if year:
            if year == 2025:
                multi_year_licences = multi_year_licences.filter(
                    MultiYearLicence.validity_end_date >= "2025-03-03",
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


class MultiYearLicenceListView(MultiYearLicenceSerializerMixin, ApiView):
    model = MultiYearLicence

    def get_queryset(self, domain, pk, **kwargs):
        undertaking = Undertaking.query.filter_by(
            domain=domain, external_id=pk
        ).first_or_404()
        return MultiYearLicence.query.filter_by(
                undertaking_id=undertaking.id, status="VALID"
        )

    def patch_multi_year_licences(self, **kwargs):
        data = []
        #TODO: implement when clarifying the use case for this endpoint
        return data

    def post(self, **kwargs):
        data = [self.serialize(u) for u in self.get_queryset(**kwargs)]
        data.extend(self.patch_multi_year_licences(**kwargs))
        return data

    def dispatch_request(self, **kwargs):
        return super(MultiYearLicenceListView, self).dispatch_request(**kwargs)


class MultiYearLicenceYearListView(MultiYearLicenceSerializerMixin, ApiView):
    model = MultiYearLicence

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(
            domain=domain, external_id=pk
        ).first_or_404()
        multi_year_licences = MultiYearLicence.query.filter_by(
                undertaking_id=undertaking.id, status="VALID"
        )
        year = int(year)
        if year == 2025:
            multi_year_licences = multi_year_licences.filter(
                MultiYearLicence.validity_end_date >= "2025-03-03",
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


    def patch_multi_year_licences(self, **kwargs):
        data = []
        #TODO: implement when clarifying the use case for this endpoint
        return data

    def post(self, **kwargs):
        data = [self.serialize(u) for u in self.get_queryset(**kwargs)]
        data.extend(self.patch_multi_year_licences(**kwargs))
        return data

    def dispatch_request(self, **kwargs):
        return super(MultiYearLicenceYearListView, self).dispatch_request(**kwargs)

