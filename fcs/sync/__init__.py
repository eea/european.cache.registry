from flask.ext.script import Manager

sync_manager = Manager()


class Unauthorized(Exception):
    pass


class InvalidResponse(Exception):
    pass


import fcs.sync.fgases
