import contextlib

import sys

from flask import request
import StringIO

from fcs.api.views import ApiView
from fcs.sync.commands import (
    bdr,
    fgases,
    fgases_debug_noneu,
    ods,
    ods_debug_noneu,
    sync_collections_title
)

from fcs.match import run, flush, verify, unverify, test, manual


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
        with stdout_redirect(StringIO.StringIO()) as output:
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
    command_func = staticmethod(fgases)


class SyncFgasesDebugNoneuView(MgmtCommand):
    command_func = staticmethod(fgases_debug_noneu)


class SyncODSView(MgmtCommand):
    command_func = staticmethod(ods)


class SyncCollectionsTitleView(MgmtCommand):
    command_func = staticmethod(sync_collections_title)


class SyncBdr(MgmtCommand):
    command_func = staticmethod(bdr)


class MatchRun(MgmtCommand):
    command_func = staticmethod(run)


class MatchFlush(MgmtCommand):
    command_func = staticmethod(flush)


class MatchVerify(MgmtCommand):
    command_func = staticmethod(verify)


class MatchUnverify(MgmtCommand):
    command_func = staticmethod(unverify)


class MatchTest(MgmtCommand):
    command_func = staticmethod(test)


class MatchManual(MgmtCommand):
    command_func = staticmethod(manual)
