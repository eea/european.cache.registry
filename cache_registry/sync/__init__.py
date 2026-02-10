from flask.cli import AppGroup

sync_manager = AppGroup("sync")

from cache_registry.sync.commands import *
