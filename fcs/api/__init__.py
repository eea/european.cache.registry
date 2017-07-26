# coding=utf-8
from flask import Blueprint
from flask.ext.script import Manager

from .candidate import *
from .commands import *
from .log import *
from .undertaking import *
from .user import *

api = Blueprint('api', __name__)
api_manager = Manager()


def register_url(prefix, url, view, name, path_name):
    api.add_url_rule(
        rule=prefix+url,
        view_func=view.as_view(name + '-' + path_name)
    )

# Undertaking

undertaking_prefix = '/undertaking/<domain>'
undertaking_name = 'company'

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list',
             view=UndertakingListView,
             path_name='list')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list-small',
             view=UndertakingListSmallView,
             path_name='list-small')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list/all',
             view=UndertakingListAllView,
             path_name='list-all')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list_by_vat/<vat>',
             view=UndertakingListByVatView,
             path_name='list-by-vat')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/filter',
             view=UndertakingFilterCountView,
             path_name='filter')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/<pk>/details',
             view=UndertakingDetailView,
             path_name='detail')

# User

user_prefix = '/user'
user_name = 'user'

register_url(prefix=user_prefix, name=user_name,
             url='/list',
             view=UserListView,
             path_name='list')

register_url(prefix=user_prefix, name=user_name,
             url='/<pk>/companies',
             view=UserCompaniesView,
             path_name='companies')

# Candidate

candidate_prefix = '/candidate/<domain>'
candidate_name = 'candidate'

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/list',
             view=CandidateList,
             path_name='list')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/list/verified',
             view=NonCandidateList,
             path_name='non-list')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/verify/<undertaking_id>/',
             view=CandidateVerify,
             path_name='verify')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/unverify/<undertaking_id>/',
             view=CandidateUnverify,
             path_name='unverify')

# Commands

command_prefix = '/sync'
command_name = 'sync'

register_url(prefix=command_prefix, name=command_name,
             url='/collections_title',
             view=SyncCollectionsTitleView,
             path_name='collections')

register_url(prefix=command_prefix, name=command_name,
             url='/fgases',
             view=SyncFgasesView,
             path_name='fgases')

register_url(prefix=command_prefix, name=command_name,
             url='/ods',
             view=SyncODSView,
             path_name='ods')

register_url(prefix=command_prefix, name=command_name,
             url='/fgases_debug_noneu',
             view=SyncFgasesDebugNoneuView,
             path_name='fgases-debug-noneu')

register_url(prefix=command_prefix, name=command_name,
             url='/ods_debug_noneu',
             view=SyncODSDebugNoneuView,
             path_name='ods-debug-noneu')

# Log

log_prefix = '/log'
log_name = 'log'


register_url(prefix=log_prefix, name=log_name,
             url='/sync',
             view=DataSyncLogsView,
             path_name='sync')


register_url(prefix=log_prefix, name=log_name,
             url='/matching',
             view=MatchingLogsView,
             path_name='matching')
