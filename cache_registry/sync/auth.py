from flask import current_app

from cache_registry.models import db, User


class Unauthorized(Exception):
    pass


class InvalidResponse(Exception):
    pass


def get_auth(user, password):
    return (
        current_app.config.get(user, "user"),
        current_app.config.get(password, "pass"),
    )


def patch_users(external_id, users, patch_dict="PATCH_USERS"):
    """Patch the list of contact persons"""
    external_id = str(external_id)
    patch = current_app.config.get(patch_dict, {})
    if external_id in patch:
        print(f"Patching company: {external_id}")
        users.extend(patch[external_id])
        return users, True
    return users, False


def cleanup_unused_users():
    """Remove users that do not have a company attached"""
    unused_users = User.query.filter_by(undertakings=None, auditors=None)

    print("Removing", unused_users.count(), "unused users")
    for u in unused_users:
        db.session.delete(u)
        current_app.logger.info(
            f"User {u.username} with email {u.email} has been deleted"
        )
