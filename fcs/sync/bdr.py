import json
import requests
from datetime import datetime

from flask import current_app

from .auth import get_auth
from .undertakings import get_absolute_url


def bdr_request(url, params=None):
    auth = get_auth('BDR_ENDPOINT_USER', 'BDR_ENDPOINT_PASSWORD')
    ssl_verify = current_app.config['HTTPS_VERIFY']

    response = None
    try:
        response = requests.get(url, params=params, auth=auth,
                                verify=ssl_verify)
    except requests.ConnectionError:
        error_message = 'BDR was unreachable - {}'.format(datetime.now())
        current_app.logger.warning(error_message)
        print error_message
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return response


def get_bdr_collections():
    endpoint = current_app.config['BDR_ENDPOINT_URL']
    url = endpoint + '/api/collections_json'
    response = bdr_request(url)
    if response and response.status_code == 200:
        return response.json()


def check_bdr_request(params, relative_url):
    url = get_absolute_url('BDR_ENDPOINT_URL', relative_url)
    response = bdr_request(url, params)
    error_message = ''
    if response is not None and response.headers.get(
            'content-type') == 'application/json':
        json_data = json.loads(response.content)
        if json_data.get('status') != 'success':
            error_message = json_data.get('message')
        elif response.status_code != 200:
            error_message = 'Invalid status code: ' + response.status_code
    else:
        error_message = 'Invalid response: ' + str(response)
    return not error_message


def call_bdr(undertaking, old_collection=False):
    if not current_app.config.get('BDR_ENDPOINT_URL'):
        current_app.logger.warning('No bdr endpoint. No bdr call.')
        return True
    params = {
        'company_id': undertaking.external_id,
        'domain': undertaking.domain,
        'country': undertaking.country_code,
        'name': undertaking.name
    }
    if old_collection:
        params['old_collection_id'] = undertaking.oldcompany_account

    relative_url = '/ReportekEngine/update_company_collection'

    return check_bdr_request(params, relative_url)
