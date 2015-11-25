import json
import requests
from datetime import datetime

from flask import current_app


def get_auth():
    return (
        current_app.config.get('BDR_ENDPOINT_USER', 'user'),
        current_app.config.get('BDR_ENDPOINT_PASSWORD', 'pass'),
    )


def get_absolute_url(url):
    return current_app.config['BDR_ENDPOINT_URL'] + url


def do_bdr_request(params):
    url = get_absolute_url('/ReportekEngine/update_company_collection')
    auth = get_auth()
    ssl_verify = current_app.config['HTTPS_VERIFY']

    error_message = ''
    response = None
    try:
        response = requests.get(url, params=params, auth=auth,
                                verify=ssl_verify)
    except requests.ConnectionError:
        error_message = 'BDR was unreachable - {}'.format(datetime.now())

    if response is not None and response.headers.get(
            'content-type') == 'application/json':
        json_data = json.loads(response.content)
        if json_data.get('status') != 'success':
            error_message = json_data.get('message')
        elif response.status_code != 200:
            error_message = 'Invalid status code: ' + response.status_code
    else:
        error_message = 'Invalid response: ' + str(response)

    if error_message:
        current_app.logger.warning(error_message)
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return not error_message


def call_bdr(undertaking, old_collection=False):
    if not current_app.config.get('BDR_ENDPOINT_URL'):
        current_app.logger.warning('No bdr endpoint. No bdr call.')
        return True
    params = {
        'company_id': undertaking.external_id,
        'domain': undertaking.domain,
        'country': undertaking.country_code,
        'name': undertaking.name,
        'date_created': undertaking.date_created
    }
    if old_collection:
        params['old_collection_id'] = undertaking.oldcompany_account
    return do_bdr_request(params)
