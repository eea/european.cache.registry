from flask import Blueprint
from flask import current_app
from .export import *
from .log import *
from .mail import *

misc = Blueprint('misc', __name__)


def register_url(prefix, url, view, name, view_name):
    misc.add_url_rule(
        rule=prefix+url,
        view_func=view.as_view(name + '-' + view_name)
    )

# Export
export_prefix = '/export'
export_name = 'export'

register_url(prefix=export_prefix, name=export_name,
             url='/undertaking/<domain>',
             view=UndertakingListExport,
             view_name='company-list')

register_url(prefix=export_prefix, name=export_name,
             url='/user/list',
             view=UserListExport,
             view_name='user-list')

register_url(prefix=export_prefix, name=export_name,
             url='/user/json',
             view=UserListExportJSON,
             view_name='user-list-json')


# Mail
mail_prefix = '/mail'
mail_name = 'mails'

register_url(prefix=mail_prefix, name=mail_name,
             url='/list',
             view=MailsList,
             view_name='list')

register_url(prefix=mail_prefix, name=mail_name,
             url='/add',
             view=MailsAdd,
             view_name='add')

register_url(prefix=mail_prefix, name=mail_name,
             url='/delete',
             view=MailsDelete,
             view_name='delete')

alert_prefix = '/alert_lockdown'
alert_name = 'alert'

register_url(prefix=alert_prefix, name=alert_name,
             url='/wrong_match',
             view=AlertWrongMatch,
             view_name='wrong-match')

register_url(prefix=alert_prefix, name=alert_name,
             url='/wrong_lockdown',
             view=AlertWrongLockdown,
             view_name='wrong-lockdown')

register_url(prefix=alert_prefix, name=alert_name,
             url='/unmatch',
             view=AlertUnmatch,
             view_name='unmatch')

# Log

log_prefix = '/log'
log_name = 'log'


register_url(prefix=log_prefix, name=log_name,
             url='/sync/<domain>',
             view=DataSyncLogsView,
             view_name='sync')


register_url(prefix=log_prefix, name=log_name,
             url='/matching/<domain>',
             view=MatchingLogsView,
             view_name='matching')


class SettingsOverview(MethodView):
    def get(self, **kwargs):
        resp = {
            'BASE_URL': current_app.config.get('BASE_URL', 'undefined'),
            'AUTO_VERIFY_COMPANIES': current_app.config.get(
                'AUTO_VERIFY_NEW_COMPANIES', False),
            'BDR_REGISTRY_URL': current_app.config['BDR_API_URL'],
        }
        return Response(json.dumps(resp, indent=2), mimetype='application/json')


misc.add_url_rule('/settings',
                  view_func=SettingsOverview.as_view(
                      'settings'))
