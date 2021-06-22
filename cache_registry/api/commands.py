import contextlib

import sys

from flask import request
from io import StringIO

from cache_registry.api.views import ApiView
from cache_registry.sync.commands import (
    call_bdr,
    call_fgases,
    call_fgases_debug_noneu,
    call_licences,
    call_ods,
    call_sync_collections_title
)

from cache_registry.match import call_run, call_flush


@contextlib.contextmanager
def stdout_redirect(where):
    sys.stdout = where
    try:
        yield where
    finally:
        sys.stdout = sys.__stdout__


class MgmtCommand(ApiView):
    command_func = None

    def get(self, **kwargs):
        kwargs = kwargs or request.args.to_dict()
        with stdout_redirect(StringIO()) as output:
            try:
                success = self.command_func(**kwargs)
                message = ''
            except Exception as ex:
                success = False
                message = repr(ex)

        output.seek(0)
        message = output.read() + message
        return {'success': success, 'message': message}


class SyncFgasesView(MgmtCommand):
    command_func = staticmethod(call_fgases)


class SyncFgasesDebugNoneuView(MgmtCommand):
    command_func = staticmethod(call_fgases_debug_noneu)


class SyncODSView(MgmtCommand):
    command_func = staticmethod(call_ods)


class SyncLicencesView(MgmtCommand):
    command_func = staticmethod(call_licences)

class SyncCollectionsTitleView(MgmtCommand):
    command_func = staticmethod(call_sync_collections_title)


class SyncBdr(MgmtCommand):
    command_func = staticmethod(call_bdr)


class MatchRun(MgmtCommand):
    command_func = staticmethod(call_run)


class MatchFlush(MgmtCommand):
    command_func = staticmethod(call_flush)
