import flask
from flask.ext.script import Manager
from fcs.models import db, db_manager
from fcs.api import api
from fcs.sync import sync_manager

DEFAULT_CONFIG = {
    'API_URL': 'http://example.com/rest/api'
}


def create_app():
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.update(DEFAULT_CONFIG)
    app.config.from_pyfile('settings.py', silent=True)
    db.init_app(app)
    app.register_blueprint(api)

    if app.config.get('SENTRY_DSN'):
        from raven.contrib.flask import Sentry

        Sentry(app)

    return app


def create_manager(app):
    manager = Manager(app)

    manager.add_command('db', db_manager)
    manager.add_command('sync', sync_manager)
    return manager
