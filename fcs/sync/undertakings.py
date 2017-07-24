import requests

from flask import current_app

from fcs.models import Undertaking, db
from .auth import get_auth, Unauthorized, InvalidResponse


def get_absolute_url(base_url, url):
    return current_app.config[base_url] + url


def get_latest_undertakings(type_url, updated_since=None):
    auth = get_auth('API_USER', 'API_PASSWORD')
    url = get_absolute_url('API_URL', type_url)
    if updated_since:
        updated_since = updated_since.strftime('%d/%m/%Y')
        params = {'updatedSince': updated_since}
    else:
        params = {}

    headers = dict(zip(('user', 'password'), auth))
    ssl_verify = current_app.config['HTTPS_VERIFY']
    response = requests.get(url, params=params, headers=headers,
                            verify=ssl_verify)

    if response.status_code == 401:
        raise Unauthorized()

    if response.status_code != 200:
        raise InvalidResponse()

    return response.json()


def patch_undertaking(external_id, data):
    external_id = str(external_id)
    patch = current_app.config.get('PATCH_COMPANIES', {})
    if external_id in patch:
        print("Patching undertaking: {}".format(external_id))
        data.update(patch[external_id])
    return data


def remove_undertaking(data):
    """Remove undertaking."""
    undertaking = (
        Undertaking.query
        .filter_by(external_id=data.get('id'))
        .first()
    )
    if undertaking:
        msg = 'Removing undertaking name: {}'\
              ' with id: {}'.format(undertaking.name, undertaking.id)
        current_app.logger.warning(msg)
        db.session.delete(undertaking)
    else:
        msg = 'No company with id: {} found in the db'.format(data.get('id'))
        current_app.logger.warning(msg)
