from flask.cli import AppGroup

sync_manager = AppGroup('sync')

import cache_registry.sync.commands
