# coding=utf-8
import datetime

from flask import current_app
from flask import request
from sqlalchemy import and_

from cache_registry.api.views import ListView, ApiView
from cache_registry.models import (
    MultiYearLicence,
    Undertaking,
    CNQuantity,
    Substance,
    MultiYearLicenceAggregated,
)


class MultiYearLicenceReturnsViewset(ListView):
    model = MultiYearLicence

    @classmethod
    def serialize(cls, obj, **kwargs):
        year = request.args.get("year")
        company_data = {"multi_year_licences": [], "aggregated_data": []}
        multi_year_licences = (
            obj.multi_year_licences.filter(
                MultiYearLicence.validity_start_date
                <= datetime.date(int(year), 12, 31),
                MultiYearLicence.validity_end_date >= datetime.date(int(year), 1, 1),
            )
            if year
            else obj.multi_year_licences
        )
        for multi_year_licence in multi_year_licences:
            cn_quantities = CNQuantity.query.filter_by(
                multi_year_licence_id=multi_year_licence.id
            )
            if year:
                cn_quantities = cn_quantities.filter_by(year=int(year))
            cn_quantities = cn_quantities.all()
            company_data["multi_year_licences"].append(
                {
                    "licence_id": multi_year_licence.licence_id,
                    "long_licence_number": multi_year_licence.long_licence_number,
                    "status": multi_year_licence.status,
                    "status_date": str(multi_year_licence.status_date),
                    "validity_start_date": str(multi_year_licence.validity_start_date),
                    "validity_end_date": str(multi_year_licence.validity_end_date),
                    "update_date": str(multi_year_licence.update_date),
                    "registration_id": multi_year_licence.undertaking.registration_id,
                    "external_id": multi_year_licence.undertaking.external_id,
                    "company_name": multi_year_licence.undertaking.name,
                    "cn_codes": [
                        {"code": cn.code, "description": cn.description}
                        for cn in multi_year_licence.cn_codes
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
                    "substances": [
                        {
                            "name": substance.name,
                            "chemical_name": substance.chemical_name,
                        }
                        for substance in multi_year_licence.substances
                    ],
                    "detailed_uses": [
                        {
                            "short_code": detailed_use.short_code,
                            "code": detailed_use.code,
                        }
                        for detailed_use in multi_year_licence.detailed_uses
                    ],
                }
            )
        multi_year_licences_aggregated = (
            obj.multi_year_licences_aggregated.filter_by(year=int(year))
            if year
            else obj.multi_year_licences_aggregated
        )
        for multi_year_licence_aggregated in multi_year_licences_aggregated:
            company_data["aggregated_data"].append(
                {
                    "year": multi_year_licence_aggregated.year,
                    "organization_country_name": multi_year_licence_aggregated.organization_country_name,
                    "substance": multi_year_licence_aggregated.substance,
                    "lic_use_kind": multi_year_licence_aggregated.lic_use_kind,
                    "lic_use_desc": multi_year_licence_aggregated.lic_use_desc,
                    "lic_type": multi_year_licence_aggregated.lic_type,
                    "license_type": multi_year_licence_aggregated.licence_type,
                    "aggregated_reserved_ods_net_mass": str(
                        multi_year_licence_aggregated.aggregated_reserved_ods_net_mass
                    ),
                    "aggregated_consumed_ods_net_mass": str(
                        multi_year_licence_aggregated.aggregated_consumed_ods_net_mass
                    ),
                    "has_certex_data": multi_year_licence_aggregated.has_certex_data,
                    "created_from_certex": multi_year_licence_aggregated.created_from_certex,
                }
            )
        return {obj.external_id: company_data}

    def get_queryset(self, **kwargs):
        external_id = request.args.get("external_id")
        year = request.args.get("year")
        try:
            external_id = int(external_id) if external_id else None
            year = int(year) if year else None
        except ValueError:
            return []
        undertakings = Undertaking.query.filter(
            Undertaking.domain == "ODS",
        )
        if year:
            undertakings = undertakings.filter(
                Undertaking.multi_year_licences.any(
                    and_(
                        MultiYearLicence.validity_start_date
                        <= datetime.date(year, 12, 31),
                        MultiYearLicence.validity_end_date >= datetime.date(year, 1, 1),
                    )
                )
            )
        if external_id:
            undertakings = undertakings.filter_by(external_id=external_id)
        return undertakings.all()


class MultiYearLicenceAggregatedSerializerMixin:

    @classmethod
    def serialize_single_year_licence(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("date_created", "date_updated", "delivery_id")
        for field in _strip_fields:
            data.pop(field)
        data["company_id"] = obj.deliverylicence.undertaking.external_id
        data["use_kind"] = data.pop("lic_use_kind")
        data["use_desc"] = data.pop("lic_use_desc")
        data["type"] = data.pop("lic_type")
        data["quantity"] = data["quantity"]
        data["is_multi_year_licence"] = False
        if data["use_desc"] != "laboratory uses":
            data["quantity"] = int(data["quantity"])
        return data

    @classmethod
    def serialize_multi_year_licence_aggregated(cls, obj, **kwargs):
        data = {}
        data.update(
            {
                "year": obj.year,
                "substance": obj.substance,
                "s_orig_country_name": "",
                "quantity": obj.aggregated_consumed_ods_net_mass,
                "organization_country_name": obj.organization_country_name,
                "company_id": obj.undertaking.external_id,
                "use_kind": obj.lic_use_kind,
                "use_desc": obj.lic_use_desc,
                "type": obj.lic_type,
                "licence_type": obj.licence_type,
                "has_certex_data": obj.has_certex_data,
                "is_multi_year_licence": True,
            }
        )
        return data

    @classmethod
    def serialize(cls, obj, **kwargs):
        if isinstance(obj, MultiYearLicenceAggregated):
            return cls.serialize_multi_year_licence_aggregated(obj, **kwargs)
        elif isinstance(obj, Substance):
            return cls.serialize_single_year_licence(obj, **kwargs)
        return ApiView.serialize(obj)


class MultiYearLicenceAggregatedListView(
    MultiYearLicenceAggregatedSerializerMixin, ApiView
):
    model = MultiYearLicence

    def get_queryset(self, domain, pk, **kwargs):
        undertaking = Undertaking.query.filter_by(
            domain=domain, external_id=pk
        ).first_or_404()
        multi_year_licences_aggregated = MultiYearLicenceAggregated.query.filter_by(
            undertaking_id=undertaking.id
        )
        single_year_licences = []
        deliveries = undertaking.deliveries.all()
        for delivery in deliveries:
            single_year_licences.extend(delivery.substances.all())
        return multi_year_licences_aggregated.all() + single_year_licences

    def patch_multi_year_licences(self, **kwargs):
        data = []
        pk = int(kwargs["pk"])
        patch = current_app.config.get("PATCH_MULTI_YEAR_LICENCES", [])
        for element in patch:
            if element.get("company_id") == pk:
                if element["use_desc"] != "laboratory uses":
                    element["quantity"] = int(element["quantity"])
                data.append(element)
        return data

    def post(self, **kwargs):
        data = [self.serialize(u) for u in self.get_queryset(**kwargs)]
        data.extend(self.patch_multi_year_licences(**kwargs))
        return data

    def dispatch_request(self, **kwargs):
        return super(MultiYearLicenceAggregatedListView, self).dispatch_request(
            **kwargs
        )


class MultiYearLicenceAggregatedYearListView(
    MultiYearLicenceAggregatedSerializerMixin, ApiView
):
    model = MultiYearLicenceAggregated

    def get_queryset(self, domain, pk, year, **kwargs):
        undertaking = Undertaking.query.filter_by(
            domain=domain, external_id=pk
        ).first_or_404()
        multi_year_licences_aggregated = MultiYearLicenceAggregated.query.filter_by(
            undertaking_id=undertaking.id, year=year
        )
        single_year_licences = []
        delivery = undertaking.deliveries.filter_by(year=year).first()
        if delivery and delivery.substances.count() > 0:
            single_year_licences = delivery.substances.all()
        return multi_year_licences_aggregated.all() + single_year_licences

    def patch_multi_year_licences(self, **kwargs):
        data = []
        year = int(kwargs["year"])
        pk = int(kwargs["pk"])
        patch = current_app.config.get("PATCH_MULTI_YEAR_LICENCES", [])
        for element in patch:
            if element.get("year") == year and element.get("company_id") == pk:
                if element["use_desc"] != "laboratory uses":
                    element["quantity"] = int(element["quantity"])
                data.append(element)
        return data

    def post(self, **kwargs):
        data = [self.serialize(u, **kwargs) for u in self.get_queryset(**kwargs)]
        data.extend(self.patch_multi_year_licences(**kwargs))
        return data

    def dispatch_request(self, **kwargs):
        return super(MultiYearLicenceAggregatedYearListView, self).dispatch_request(
            **kwargs
        )
