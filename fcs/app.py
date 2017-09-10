import logging

import flask
from flask_script import Manager
from fcs.models import db, db_manager
from fcs.api import api, api_manager
from fcs.misc import misc
from fcs.sync import sync_manager
from fcs.match import match_manager
from fcs.manager import utils_manager
from fcs.admin import admin

DEFAULT_CONFIG = {
    'API_URL': 'http://example.com/rest/api',
    'BDR_API_URL': 'http://example.com/api',
    'HTTPS_VERIFY': None,
    'SEND_MATCHING_MAILS': False
}


def create_app(config={}):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.update(DEFAULT_CONFIG)
    if not config:
        app.config.from_pyfile('settings.py', silent=True)
    else:
        app.config.update(config)
    db.init_app(app)
    app.register_blueprint(api)
    app.register_blueprint(misc)
    admin.init_app(app)
    create_logger(app)

    if app.config.get('SENTRY_DSN'):
        from raven.contrib.flask import Sentry

        Sentry(app)

    return app


def create_logger(app):
    log_file = app.config.get('LOG_FILE', 'log_file.log')
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.WARNING)
    app.logger.addHandler(file_handler)
    file_handler.setFormatter(logging.Formatter('''
    Message [%(asctime)s]:
    %(message)s
    '''))


def create_manager(app):
    manager = Manager(app)

    manager.add_command('db', db_manager)
    manager.add_command('sync', sync_manager)
    manager.add_command('api', api_manager)
    manager.add_command('match', match_manager)
    manager.add_command('utils', utils_manager)
    return manager
