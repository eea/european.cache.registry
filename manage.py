#!/usr/bin/env python

import logging
from fcs.app import create_app, create_manager

app = create_app()


def main():
    logging.basicConfig(loglevel=logging.DEBUG)
    logging.getLogger('werkzeug').setLevel(logging.INFO)
    manager = create_manager(app)
    manager.run()


if __name__ == "__main__":
    main()
