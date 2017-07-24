
from flask import current_app

from fcs.models import db, User


def get_auth(user, password):
    return (
        current_app.config.get(user, 'user'),
        current_app.config.get(password, 'pass'),
    )


def patch_users(external_id, users):
    """ Patch the list of contact persons
    """
    external_id = str(external_id)
    patch = current_app.config.get('PATCH_USERS', {})
    if external_id in patch:
        print("Patching company: {}".format(external_id))
        users.extend(patch[external_id])
    return users


def cleanup_unused_users():
    """ Remove users that do not have a company attached """
    unused_users = User.query.filter_by(undertakings=None)

    print "Removing", unused_users.count(), "unused users"
    for u in unused_users:
        db.session.delete(u)
        current_app.logger.info(
            'User {} with email {} has been deleted'.format(
                u.username, u.email))
