import logging

import sys
import flask
from flask_migrate import Migrate

from cache_registry.models import db
from cache_registry.api import api, api_manager
from cache_registry.misc import misc
from cache_registry.sync import sync_manager
from cache_registry.match import match_manager
from cache_registry.manager import utils_manager
from cache_registry.admin import admin
from cache_registry.debug_sql import sql_debug

DEFAULT_CONFIG = {
    'API_URL': 'http://example.com/rest/api',
    'BDR_API_URL': 'http://example.com/api',
    'HTTPS_VERIFY': None,
    'SEND_MATCHING_MAILS': False
}

def init_config(app):
    try:
        default_format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
        default_datefmt = '%d-%m-%Y %H:%M'
        logging.basicConfig(level=logging.DEBUG,
                            format=default_format,
                            datefmt=default_datefmt)
        logging.getLogger('werkzeug').setLevel(logging.INFO)
        create_cli_commands(app)
    except Exception as e:
        if app.config['DEBUG'] or not app.config.get('SENTRY_DSN'):
            raise
        else:
            if not (isinstance(e, SystemExit) and e.code == 0):
                sentry = app.extensions['sentry']
                sentry.captureException()


def create_app(config={}):
    app = flask.Flask(__name__, instance_relative_config=True)
    app.config.update(DEFAULT_CONFIG)
    if not config:
        app.config.from_pyfile('settings.py', silent=True)
    else:
        app.config.update(config)
    init_config(app)
    migrate = Migrate()
    db.init_app(app)
    migrate.init_app(app, db)
    app.register_blueprint(api)
    app.register_blueprint(misc)
    admin.init_app(app)
    create_logger(app)
    if app.config.get('SENTRY_DSN'):
        from raven.contrib.flask import Sentry

        Sentry(app, dsn=app.config.get('SENTRY_DSN'),
               logging=True, level=logging.ERROR)

    if app.config.get('DEBUG') and 'testsuite' not in sys.argv:
        app.after_request(sql_debug)
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


def create_cli_commands(app):
    app.cli.add_command(api_manager)
    app.cli.add_command(match_manager)
    app.cli.add_command(sync_manager)
    app.cli.add_command(utils_manager)
