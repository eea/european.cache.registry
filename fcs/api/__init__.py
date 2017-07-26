# coding=utf-8
from flask import Blueprint
from flask.ext.script import Manager

from .candidate import *
from .commands import *
from .undertaking import *
from .user import *

api = Blueprint('api', __name__)
api_manager = Manager()


def register_url(prefix, url, view, name, view_name):
    api.add_url_rule(
        rule=prefix+url,
        view_func=view.as_view(name + '-' + view_name)
    )

# Undertaking

undertaking_prefix = '/undertaking/<domain>'
undertaking_name = 'company'

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list',
             view=UndertakingListView,
             view_name='list')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list-small',
             view=UndertakingListSmallView,
             view_name='list-small')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list/all',
             view=UndertakingListAllView,
             view_name='list-all')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/list_by_vat/<vat>',
             view=UndertakingListByVatView,
             view_name='list-by-vat')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/filter',
             view=UndertakingFilterCountView,
             view_name='filter')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/<pk>/details',
             view=UndertakingDetailView,
             view_name='detail')

register_url(prefix=undertaking_prefix, name=undertaking_name,
             url='/<pk>/statusupdate',
             view=UndertakingStatusUpdate,
             view_name='statusupdate')

# User

user_prefix = '/user'
user_name = 'user'

register_url(prefix=user_prefix, name=user_name,
             url='/list',
             view=UserListView,
             view_name='list')

register_url(prefix=user_prefix, name=user_name,
             url='/<pk>/companies',
             view=UserCompaniesView,
             view_name='companies')

# Candidate

candidate_prefix = '/candidate/<domain>'
candidate_name = 'candidate'

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/list',
             view=CandidateList,
             view_name='list')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/list/verified',
             view=NonCandidateList,
             view_name='non-list')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/verify/<undertaking_id>/',
             view=CandidateVerify,
             view_name='verify')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/unverify/<undertaking_id>/',
             view=CandidateUnverify,
             view_name='unverify')

# Commands

command_prefix = '/sync'
command_name = 'sync'

register_url(prefix=command_prefix, name=command_name,
             url='/collections_title',
             view=SyncCollectionsTitleView,
             view_name='collections')

register_url(prefix=command_prefix, name=command_name,
             url='/fgases',
             view=SyncFgasesView,
             view_name='fgases')

register_url(prefix=command_prefix, name=command_name,
             url='/ods',
             view=SyncODSView,
             view_name='ods')

register_url(prefix=command_prefix, name=command_name,
             url='/fgases_debug_noneu',
             view=SyncFgasesDebugNoneuView,
             view_name='fgases-debug-noneu')

register_url(prefix=command_prefix, name=command_name,
             url='/ods_debug_noneu',
             view=SyncODSDebugNoneuView,
             view_name='ods-debug-noneu')
