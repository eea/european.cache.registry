from .factories import UserFactory
from cache_registry import models

from cache_registry.sync.auth import cleanup_unused_users


def test_cleanup_unused_users(client):
    UserFactory(username="user1")
    UserFactory(username="user2")
    assert models.User.query.count() == 2
    cleanup_unused_users()
    assert models.User.query.count() == 0
