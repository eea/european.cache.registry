import ast
import json
import requests
from datetime import datetime

from flask import current_app

from .auth import get_auth


def get_absolute_url(base_url, url):
    return current_app.config[base_url] + url


def do_bdr_request(url, params=None):
    auth = get_auth('BDR_ENDPOINT_USER', 'BDR_ENDPOINT_PASSWORD')
    ssl_verify = current_app.config['HTTPS_VERIFY']

    response = None
    try:
        response = requests.get(url, params=params, auth=auth,
                                verify=ssl_verify)
    except requests.ConnectionError:
        error_message = 'BDR was unreachable - {}'.format(datetime.now())
        current_app.logger.warning(error_message)
        print(error_message)
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return response


def get_bdr_collections():
    endpoint = current_app.config['BDR_ENDPOINT_URL']
    url = endpoint + '/api/collections_json'
    response = do_bdr_request(url)
    if response and response.status_code == 200:
        return response.json()


def check_bdr_request(params, relative_url):
    url = get_absolute_url('BDR_ENDPOINT_URL', relative_url)
    response = do_bdr_request(url, params)
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


def update_bdr_col_name(undertaking):
    """ Update the BDR collection name with the new name
        For the moment, use the API script in the BDR's api/
        folder in order to change the name. This should be changed
        in the future to use a unified API for registries
    """
    DOMAIN_TO_ZOPE_FOLDER = {
        'FGAS': 'fgases',
        'ODS': 'ods'
    }
    endpoint = current_app.config['BDR_ENDPOINT_URL']
    if not endpoint:
        current_app.logger.warning('No bdr endpoint. No bdr call.')
        return True

    params = {
        'country_code': undertaking.country_code.lower(),
        'obligation_folder_name': DOMAIN_TO_ZOPE_FOLDER.get(undertaking.domain),
        'account_uid': str(undertaking.external_id),
        'organisation_name': undertaking.name,
        'oldcompany_account': undertaking.oldcompany_account
    }

    url = endpoint + '/api/update_organisation_name'
    response = do_bdr_request(url, params)
    error_message = ''
    if response is not None:
        try:
            res = ast.literal_eval(response.content)
        except:
            res = {}
        if not res.get('updated') is True:
            error_message = 'Collection for id: {0} not updated'\
                            .format(undertaking.external_id)
        elif response.status_code != 200:
            error_message = 'Invalid status code: ' + response.status_code
    else:
        error_message = 'Invalid response: ' + str(response)

    if error_message:
        current_app.logger.warning(error_message)
        print(error_message)
        if 'sentry' in current_app.extensions:
            current_app.extensions['sentry'].captureMessage(error_message)

    return not error_message
