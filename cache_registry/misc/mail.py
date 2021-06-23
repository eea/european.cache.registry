import json

from flask import request

from cache_registry.api.views import ListView, ApiView
from cache_registry.mails import (
    send_wrong_match_mail,
    send_wrong_lockdown_mail,
    send_unmatch_mail,
)
from cache_registry.models import MailAddress, db


class MailsList(ListView):
    model = MailAddress


class MailsAdd(ApiView):
    def post(self):
        mail = request.form["mail"]
        if MailAddress.query.filter_by(mail=mail).all():
            return {"success": False, "message": "This email address already exists"}
        contact = MailAddress(
            mail=mail,
            first_name=request.form["first_name"],
            last_name=request.form["last_name"],
        )
        db.session.add(contact)
        db.session.commit()
        return {"success": True}


class MailsDelete(ApiView):
    def post(self):
        mail = request.form["mail"]
        contact = MailAddress.query.filter_by(mail=mail).all()
        if not contact:
            return json.dumps(
                {"success": False, "message": "This email address does not exists"}
            )
        db.session.delete(contact[0])
        db.session.commit()
        return json.dumps(
            {
                "success": True,
            }
        )


class AlertWrongMatch(ApiView):
    def post(self, **kwargs):
        resp = send_wrong_match_mail(
            request.form["user"], request.form["company_id"], kwargs["domain"]
        )
        return json.dumps(resp)


class AlertWrongLockdown(ApiView):
    def post(self, **kwargs):
        resp = send_wrong_lockdown_mail(
            request.form["user"], request.form["company_id"], kwargs["domain"]
        )
        return json.dumps(resp)


class AlertUnmatch(ApiView):
    def post(self, **kwargs):
        resp = send_unmatch_mail(
            request.form["user"],
            request.form["company_id"],
            request.form["old_company"],
            request.form["oldcollection_path"],
            kwargs["domain"],
        )
        return json.dumps(resp)
