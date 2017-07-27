import json

from flask import request

from fcs.api.views import ListView, ApiView
from fcs.mails import (
    send_wrong_match_mail,
    send_wrong_lockdown_mail,
    send_unmatch_mail
)
from fcs.models import MailAddress, db


class MailsList(ListView):
    model = MailAddress


class MailsAdd(ApiView):
    def post(self):
        mail = request.form['mail']
        if MailAddress.query.filter_by(mail=mail).all():
            return json.dumps({
                'success': False,
                'message': 'This email address already exists'
            })
        contact = MailAddress(mail=mail,
                              first_name=request.form['first_name'],
                              last_name=request.form['last_name'])
        db.session.add(contact)
        db.session.commit()
        return json.dumps({
            'success': True
        })


class MailsDelete(ApiView):
    def post(self):
        mail = request.form['mail']
        contact = MailAddress.query.filter_by(mail=mail).all()
        if not contact:
            return json.dumps({
                'success': False,
                'message': 'This email address does not exists'
            })
        db.session.delete(contact[0])
        db.session.commit()
        return json.dumps({
            'success': True,
        })


class AlertWrongMatch(ApiView):
    def post(self):
        resp = send_wrong_match_mail(request.form['user'],
                                     request.form['company_id'])
        return json.dumps(resp)


class AlertWrongLockdown(ApiView):
    def post(self):
        resp = send_wrong_lockdown_mail(request.form['user'],
                                        request.form['company_id'])
        return json.dumps(resp)


class AlertUnmatch(ApiView):
    def post(self):
        resp = send_unmatch_mail(request.form['user'],
                                 request.form['company_id'],
                                 request.form['old_company'],
                                 request.form['oldcollection_path'])
        return json.dumps(resp)
