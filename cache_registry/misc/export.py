from io import BytesIO
import json
from openpyxl import Workbook
from tempfile import NamedTemporaryFile

from flask import Response
from flask.views import MethodView

from cache_registry.api.undertaking import UndertakingListView
from cache_registry.match import get_all_non_candidates
from cache_registry.models import User

MIME_TYPE = "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"


class UndertakingListExport(MethodView):

    COLUMNS = {
        "company_id": "company_id",
        "registration_id": "registration_id",
        "name": "name",
        "domain": "domain",
        "status": "status",
        "undertaking_type": "undertaking_type",
        "website": "website",
        "date_updated": "date_updated",
        "phone": "phone",
        "oldcompany_extid": "oldcompany_extid",
        "address_city": "address_city",
        "address_country_code": "address_country_code",
        "address_country_name": "address_country_name",
        "address_country_type": "address_country_type",
        "address_zipcode": "address_zipcode",
        "address_number": "address_number",
        "address_street": "address_street",
        "country_code": "country_code",
        "vat": "vat_number",
        "eori_number": "eori_number",
        "users": "users",
        "types": "types",
        "collection_id": "collection_id",
        "date_created": "date_created",
        "oldcompany_account": "oldcompany_account",
        "oldcompany_verified": "oldcompany_verified",
        "representative_name": "representative_name",
        "representative_contact_first_name": "representative_contact_first_name",
        "representative_contact_last_name": "representative_contact_last_name",
        "check_passed": "check_passed",
        "representative_vatnumber": "representative_vatnumber",
        "representative_contact_email": "representative_contact_email",
        "representative_address_zipcode": "representative_address_zipcode",
        "representative_address_number": "representative_address_number",
        "representative_address_street": "representative_address_street",
        "representative_address_city": "representative_address_city",
        "representative_address_country_code": "representative_address_country_code",
        "representative_address_country_type": "representative_address_country_type",
        "representative_address_country_name": "representative_address_country_name",
        "represent_history": "represent_history",
    }

    def get_data(self, domain):
        return [
            UndertakingListView.serialize(c) for c in get_all_non_candidates(domain)
        ]

    def parse_column(self, qs, column):
        def _parse_address(qs, column):
            for sub_column in column.split("_"):
                qs = qs[sub_column]
            return qs

        if column.startswith("address"):
            return _parse_address(qs, column)
        elif column.startswith("representative"):
            repr_info = column.split("_", 1)[1]
            qs = qs["representative"]
            if not qs:
                return None
            if repr_info.startswith("address"):
                return _parse_address(qs, repr_info)
            return qs[repr_info]
        return qs[column]

    def get(self, domain, **kwargs):
        queryset = self.get_data(domain)
        if domain == "ODS":
            self.COLUMNS["vat"] = "eori_number"
            self.COLUMNS.pop("eori_number")

        wb = Workbook()
        ws = wb.active
        ws.title = "Companies List"
        ws.append([value for _, value in self.COLUMNS.items()])
        for qs in queryset:
            qs["users"] = ", ".join([user["username"] for user in qs["users"]])
            qs["represent_history"] = ", ".join(
                [repr["name"] for repr in qs["represent_history"]]
            )
            values = [self.parse_column(qs, key) for key, _ in self.COLUMNS.items()]
            ws.append(values)
        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            response = Response(BytesIO(tmp.read()), mimetype=MIME_TYPE)
            response.headers.add(
                "Content-Disposition", "attachment; filename=companies_list.xlsx"
            )
            return response


class UserListExport(MethodView):
    COLUMNS = [
        "username",
        "companyname",
        "country",
        "contact_firstname",
        "contact_lastname",
        "contact_email",
    ]

    def get(self, **kwargs):
        users = User.query.all()

        wb = Workbook()
        ws = wb.active
        ws.title = "Users List"
        ws.append(self.COLUMNS)
        for user in users:
            companies_with_domain = user.verified_undertakings.filter_by(
                domain=kwargs["domain"]
            )
            for company in companies_with_domain:
                for cp in company.contact_persons:
                    if cp.username == user.username:
                        values = [
                            user.username,
                            company.name,
                            company.address.country.name,
                            cp.first_name,
                            cp.last_name,
                            cp.email,
                        ]
                        ws.append(values)

        with NamedTemporaryFile() as tmp:
            wb.save(tmp.name)
            response = Response(BytesIO(tmp.read()), mimetype=MIME_TYPE)
            response.headers.add(
                "Content-Disposition", "attachment; filename=users_list.xlsx"
            )
            return response


class UserListExportJSON(MethodView):
    def get(self, **kwargs):
        users = User.query.all()

        resp = []
        for user in users:
            companies_with_domain = user.verified_undertakings.filter_by(
                domain=kwargs["domain"]
            )
            for company in companies_with_domain:
                for cp in company.contact_persons:
                    if cp.username == user.username:
                        resp.append(
                            {
                                "username": user.username,
                                "companyname": company.name,
                                "country": company.address.country.name,
                                "ecas_id": cp.ecas_id,
                                "contact_firstname": cp.first_name,
                                "contact_lastname": cp.last_name,
                                "contact_email": cp.email,
                            }
                        )
        return Response(json.dumps(resp, indent=2), mimetype="application/json")
