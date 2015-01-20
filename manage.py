#!/usr/bin/env python

import logging
from fcs.app import create_app, create_manager

app = create_app()


def main():
    default_format = '%(asctime)s - %(name)s - %(levelname)s: %(message)s'
    default_datefmt = '%d-%m-%Y %H:%M'
    logging.basicConfig(loglevel=logging.DEBUG,
                        format=default_format,
                        datefmt=default_datefmt)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    manager = create_manager(app)
    manager.run()


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        if app.config['DEBUG'] or not app.config.get('SENTRY_DSN'):
            raise
        else:
            if not (isinstance(e, SystemExit) and e.code == 0):
                sentry = app.extensions['sentry']
                sentry.captureException()
