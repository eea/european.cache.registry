import smtplib

from flask.ext.mail import Mail, Message
from flask import current_app as app


def send_mail(subject, html):
    recipients = app.config.get('NOTIFY_EMAILS')
    sender = 'Eau de Web <%s>' % app.config.get('MAIL_USERNAME')
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