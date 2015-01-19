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
    main()
