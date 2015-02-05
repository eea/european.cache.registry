import smtplib

from flask.ext.mail import Mail, Message
from flask import current_app as app, render_template

from fcs.models import MailAddress


def send_mail(subject, html, recipients):
    sender = app.config.get('MAILS_SENDER_NAME', 'BDR Help Desk')
    message = Message(subject=subject, recipients=recipients, html=html,
                      sender=sender)
    mail = Mail(app)
    try:
        mail.send(message)
        return True
    except smtplib.SMTPAuthenticationError:
        print 'Wrong username/password. ' + \
            'Please review their values in settings.py'
        return False


def send_match_mail(match, **kwargs):
    if not app.config.get('SEND_MATCHING_MAILS'):
        return
    host = app.config.get('BDR_HOST')
    if not host:
        message = 'No BDR_HOST was set in order to send notification emails. ' \
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
        recipients = [contact.mail]
        send_mail(subject, html, recipients)
