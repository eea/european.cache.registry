# coding=utf-8
from collections import defaultdict
from datetime import datetime

from flask import request
from sqlalchemy import func

from cache_registry.api.serializers import (
    AddressDetail,
    AuditorDetail,
    AuditorUndertakingDetail,
)
from cache_registry.api.views import ApiView, DetailView, ListView
from cache_registry.api.user import UserListView
from cache_registry.models import Auditor, AuditorUndertaking, db, Undertaking, User


class AuditorListView(ListView):
    model = Auditor

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("address_id",)
        for field in _strip_fields:
            data.pop(field)
        data.update(
            {
                "ms_accreditation_issuing_countries": [
                    country.code for country in obj.ms_accreditation_issuing_countries
                ],
                "address": AddressDetail.serialize(obj.address),
                "users": [UserListView.serialize(cp) for cp in obj.contact_persons],
                "audited_companies": [
                    AuditorUndertakingDetail.serialize(au)
                    for au in obj.auditor_undertakings
                ],
            }
        )
        return data


class AuditorDetailView(DetailView):
    model = Auditor

    def get_object(self, pk, **kwargs):
        return self.model.query.filter_by(auditor_uid=pk).first_or_404()

    @classmethod
    def serialize(cls, obj, **kwargs):
        data = ApiView.serialize(obj)
        _strip_fields = ("address_id",)
        for field in _strip_fields:
            data.pop(field)
        data.update(
            {
                "ms_accreditation_issuing_countries": [
                    country.code for country in obj.ms_accreditation_issuing_countries
                ],
                "address": AddressDetail.serialize(obj.address),
                "users": [UserListView.serialize(cp) for cp in obj.contact_persons],
                "audited_companies": [
                    AuditorUndertakingDetail.serialize(au)
                    for au in obj.auditor_undertakings
                ],
            }
        )
        return data


class AuditorCheckAccessMixin:

    def check_access_to_auditor(self, undertaking, auditor_uid):
        errors = defaultdict(list)
        auditor = Auditor.query.filter_by(auditor_uid=auditor_uid).first()
        if not auditor:
            errors["auditor"].append("Auditor not found")
        else:
            if auditor.status.value != "VALID":
                errors["auditor"].append("Auditor is not valid")
            if not auditor.ets_accreditation:
                if undertaking.country_code not in [
                    country.code
                    for country in auditor.ms_accreditation_issuing_countries
                ]:
                    errors["auditor"].append(
                        "Auditor is not accredited for this country"
                    )
        if errors:
            return False, None, errors
        return True, auditor, errors


class AuditorCheckView(ApiView, AuditorCheckAccessMixin):
    model = Auditor

    def serialize(self, obj, access, **kwargs):
        auditor = AuditorDetail.serialize(obj)
        data = {"access": access, "auditor": auditor}
        return data

    def get(self, domain, external_id, auditor_uid, **kwargs):
        # only FGAS domain is supported
        if domain != "FGAS":
            return {"error": "Invalid domain"}
        undertaking = Undertaking.query.filter_by(
            external_id=external_id
        ).first_or_404()

        access, auditor, errors = self.check_access_to_auditor(undertaking, auditor_uid)
        if not auditor:
            return {
                "access": False,
                "auditor": None,
                "errors": errors,
            }
        return self.serialize(
            auditor,
            access=access,
            domain=domain,
            external_id=external_id,
            auditor_uid=auditor_uid,
            **kwargs,
        )


class AuditorAssignView(ApiView, AuditorCheckAccessMixin):
    model = Auditor

    def validate_data(self, undertaking, auditor, data):
        errors = defaultdict(list)
        validate = True

        if "email" not in data:
            validate = False
            errors["email"].append("Email is required")
        else:
            if not data["email"] in [cp.email for cp in auditor.contact_persons]:
                validate = False
                errors["email"].append("User not found")
        if not data.get("reporting_envelope_url", None):
            validate = False
            errors["reporting_envelope_url"].append(
                "Reporting envelope URL is required"
            )
        if not data.get("verification_envelope_url", None):
            validate = False
            errors["verification_envelope_url"].append(
                "Verification envelope URL is required"
            )
        access, auditor, access_errors = self.check_access_to_auditor(
            undertaking, auditor.auditor_uid
        )
        if not access:
            validate = False
            errors.update(access_errors)
        if validate:
            user = User.query.filter(
                User.email == data["email"], User.auditors.contains(auditor)
            ).first()
            if AuditorUndertaking.query.filter_by(
                undertaking=undertaking,
                auditor=auditor,
                user=user,
                reporting_envelope_url=data["reporting_envelope_url"],
                verification_envelope_url=data["verification_envelope_url"],
                end_date=None,
            ).first():
                validate = False
                errors["auditor"].append("Auditor already assigned")
            if AuditorUndertaking.query.filter_by(
                undertaking=undertaking,
                end_date=None,
                verification_envelope_url=data["verification_envelope_url"],
            ).first():
                validate = False
                errors["auditor"].append(
                    "Verification envelope already has an auditor assigned"
                )

        return validate, errors

    def post(self, domain, external_id, auditor_uid, **kwargs):
        data = request.get_json()
        undertaking = Undertaking.query.filter_by(
            external_id=external_id, domain=domain
        ).first_or_404()
        auditor = Auditor.query.filter_by(auditor_uid=auditor_uid).first_or_404()
        validated, errors = self.validate_data(undertaking, auditor, data)
        if not validated:
            self.status_code = 400
            return {"errors": errors, "success": False}

        user = User.query.filter_by(email=data["email"]).first()
        auditor_undertaking = AuditorUndertaking(
            auditor=auditor,
            undertaking=undertaking,
            user=user,
            start_date=datetime.now(),
            reporting_envelope_url=data["reporting_envelope_url"],
            verification_envelope_url=data["verification_envelope_url"],
        )
        db.session.add(auditor_undertaking)
        db.session.commit()
        return {"success": True, "errors": []}


class AuditorUnassignView(ApiView):
    model = Auditor

    def validate_data(self, undertaking, auditor, data):
        required_fields = [
            "email",
            "reporting_envelope_url",
            "verification_envelope_url",
        ]
        errors = defaultdict(list)
        validate = True
        for field in required_fields:
            if not data.get(field, None):
                validate = False
                errors[field].append("This field is required")
        return validate, errors

    def post(self, domain, external_id, auditor_uid, **kwargs):
        undertaking = Undertaking.query.filter_by(
            external_id=external_id, domain=domain
        ).first_or_404()
        auditor = Auditor.query.filter_by(auditor_uid=auditor_uid).first_or_404()
        data = request.get_json()
        validated, errors = self.validate_data(undertaking, auditor, data)
        if not validated:
            self.status_code = 400
            return {"errors": errors}
        user = User.query.filter(
            User.email == data["email"], User.auditors.contains(auditor)
        ).first()
        if not user:
            self.status_code = 400
            return {"errors": {"email": ["User not found"]}}
        auditor_undertaking = AuditorUndertaking.query.filter_by(
            auditor=auditor,
            undertaking=undertaking,
            end_date=None,
            user=user,
            reporting_envelope_url=data["reporting_envelope_url"],
            verification_envelope_url=data["verification_envelope_url"],
        ).first_or_404()

        auditor_undertaking.end_date = datetime.now()
        db.session.add(auditor_undertaking)
        db.session.commit()
        return {"success": True}


class AuditorVerificationEnvelopesView(ApiView):
    model = AuditorUndertaking

    def serialize(self, objs, **kwargs):
        data = {
            "verification_envelopes": [
                AuditorUndertakingDetail.serialize(obj) for obj in objs
            ]
        }
        return data

    def get(self, **kwargs):
        if "reporting_envelope_url" not in request.args:
            self.status_code = 400
            return {"error": "reporting_envelope_url query parameter is required"}

        reporting_envelope_url = request.args.get("reporting_envelope_url")
        trimmed_reporting_envelope_url = reporting_envelope_url.strip("/").rstrip("/")
        objs = AuditorUndertaking.query.filter(
            func.rtrim(func.ltrim(AuditorUndertaking.reporting_envelope_url, "/"), "/")
            == trimmed_reporting_envelope_url
        ).all()

        return self.serialize(
            objs,
            **kwargs,
        )
