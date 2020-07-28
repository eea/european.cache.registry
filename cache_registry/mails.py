import smtplib

from flask_mail import Mail, Message
from flask import current_app as app, render_template

from cache_registry.models import (
    MailAddress,
    Undertaking,
    OldCompany,
    OldCompanyLink
)


def send_mail(subject, html, recipients):
    sender = app.config.get('MAILS_SENDER_NAME', 'BDR Help Desk')
    message = Message(subject=subject, recipients=recipients, html=html,
                      sender=sender)
    mail = Mail(app)
    try:
        mail.send(message)
        return True
    except smtplib.SMTPAuthenticationError:
        print('Wrong username/password. ' \
              'Please review their values in settings.py')
        return False


def send_match_mail(match, **kwargs):
    if not app.config.get('SEND_MATCHING_MAILS'):
        return
    host = app.config.get('BDR_ENDPOINT_URL')
    if not host:
        message = 'No BDR_ENDPOINT_URL was set in order to send notification emails. ' \
                  'Please set this value or disable mails sending.'
        app.logger.warning(message)
        if 'sentry' in app.extensions:
            app.extensions['sentry'].captureMessage(message)
        return
    if match:
        template = 'mails/match_notification.html'
        subject = "BDR - New Company matched"
    else:
        template = 'mails/no_match_notification.html'
        subject = "BDR - New Company added"

    for contact in MailAddress.query.all():
        kwargs.update({
            'first_name': contact.first_name,
            'last_name': contact.last_name,
        })
        html = render_template(template, host=host, **kwargs)
        send_mail(subject, html, [contact.mail])


def send_mail_to_list(template, subject, kwargs):
    for contact in MailAddress.query.all():
        kwargs.update({'first_name': contact.first_name,
                       'last_name': contact.last_name})
        html = render_template(template, **kwargs)
        send_mail(subject, html, [contact.mail])


def send_wrong_match_mail(user, company_id, domain):
    template = 'mails/wrong_match.html'
    subject = 'BDR - Wrong match alert'
    hd = app.config.get('BDR_HELP_DESK_MAIL')
    if not hd:
        message = 'No BDR_HELP_DESK_MAIL was set in order to send the wrong '\
                  'match email alert. Please set this value and try again.'
        app.logger.warning(message)
        if 'sentry' in app.extensions:
            app.extensions['sentry'].captureMessage(message)
        return False

    company = Undertaking.query.filter_by(
        external_id=company_id,
        domain=domain
    ).first()
    link = OldCompanyLink.query.filter_by(
        undertaking=company
    ).first()
    kwargs = {
        'user': user,
        'bdr_help_desk_email': hd,
        'company_name': company.name,
        'oldcompany_name': link.oldcompany.name,
        'domain': domain,
    }
    send_mail_to_list(template, subject, kwargs)
    return True


def send_wrong_lockdown_mail(user, company_id, domain):
    template = 'mails/wrong_lockdown.html'
    subject = 'BDR - Wrong lockdown alert'
    company = Undertaking.query.filter_by(
        external_id=company_id,
        domain=domain
    ).first()
    link = OldCompanyLink.query.filter_by(
        undertaking=company
    ).first()
    kwargs = {
        'user': user,
        'company_name': company.name,
        'oldcompany_name': link.oldcompany.name,
        'domain': domain,
    }
    send_mail_to_list(template, subject, kwargs)
    return True


def send_unmatch_mail(user, company_id, oldcompany_id, oldcollection_path,
                      domain):
    template = 'mails/unmatch.html'
    subject = 'BDR - Unmatch alert'
    company = Undertaking.query.filter_by(
        external_id=company_id,
        domain=domain
    ).first()
    oldcompany = OldCompany.query.filter_by(
        external_id=oldcompany_id
    ).first()
    kwargs = {
        'user': user,
        'company_name': company.name,
        'oldcompany_name': oldcompany.name,
        'oldcollection_path': oldcollection_path,
        'domain': domain,
    }
    send_mail_to_list(template, subject, kwargs)
    return True
