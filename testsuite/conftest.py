from pytest import fixture
from flask_webtest import TestApp

from cache_registry.app import create_app
from cache_registry.models import db
from cache_registry.models import loaddata

from instance.settings import FGAS, ODS

TEST_CONFIG = {
    "DEBUG": True,
    "SERVER_NAME": "noname",
    "BDR_ENDPOINT_URL": "",
    "BDR_ENDPOINT_USER": "user",
    "BDR_ENDPOINT_PASSWORD": "password",
    "AUTO_VERIFY_NEW_COMPANIES": [FGAS],
    "AUTO_VERIFY_ALL_COMPANIES": [],
    "SENTRY_DSN": "",
    "BDR_HELP_DESK_MAIL": "test-mail",
    "LOG_FILE": "test.log",
    "MANUAL_VERIFY_ALL_COMPANIES": [FGAS, ODS],
    "MAIL_SERVER": "localhost",
    "MAIL_PORT": 25,
    "SQLALCHEMY_DATABASE_URI": "sqlite:///:memory:",
    "SQLALCHEMY_TRACK_MODIFICATIONS": False,
    "TESTING": True,
}


def create_testing_app():
    test_config = dict(TEST_CONFIG)

    app = create_app(test_config)
    return app


@fixture
def app(request):
    app = create_testing_app()
    app_context = app.app_context()
    app_context.push()
    db.create_all()
    loaddata("cache_registry/fixtures/types.json")
    loaddata("cache_registry/fixtures/business_profiles.json")

    @request.addfinalizer
    def fin():
        app_context.pop()

    return app


@fixture
def client(app):
    client = TestApp(app)
    return client
