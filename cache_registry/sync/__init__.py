from flask_script import Manager

sync_manager = Manager()

import cache_registry.sync.commands
