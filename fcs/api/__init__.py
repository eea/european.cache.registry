# coding=utf-8
from flask import Blueprint
from flask_script import Manager

from .candidate import *
from .commands import *
from .old_company import *
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
             url='/verify/<undertaking_id>/<oldcompany_id>',
             view=CandidateVerify,
             view_name='verify')

register_url(prefix=candidate_prefix, name=candidate_name,
             url='/unverify/<undertaking_id>/',
             view=CandidateUnverify,
             view_name='unverify')
register_url(prefix=candidate_prefix, name=candidate_name,
             view=CandidateVerifyNone,
             url='/verify-none/<undertaking_id>',
             view_name='verify_none')
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
             url='/bdr',
             view=SyncBdr,
             view_name='sync-bdr')

register_url(prefix=command_prefix, name=command_name,
             url='/fgases_debug_noneu',
             view=SyncFgasesDebugNoneuView,
             view_name='fgases-debug-noneu')

# Old companies
command_prefix = '/oldcompanies'
command_name = 'oldcompany'

register_url(prefix=command_prefix, name=command_name,
             url='/list/valid/',
             view=OldCompanyListValid,
             view_name='list-valid')

register_url(prefix=command_prefix, name=command_name,
             url='/list/invalid/',
             view=OldCompanyListInvalid,
             view_name='list-invalid')

register_url(prefix=command_prefix, name=command_name,
             url='/<pk>/valid/',
             view=OldCompanySetValid,
             view_name='set-valid')

register_url(prefix=command_prefix, name=command_name,
             url='/<pk>/invalid/',
             view=OldCompanySetInvalid,
             view_name='set-invalid')

# Match
command_prefix = '/match'
command_name = 'match'

register_url(prefix=command_prefix, name=command_name,
             url='/run',
             view=MatchRun,
             view_name='run')

register_url(prefix=command_prefix, name=command_name,
             url='/flush',
             view=MatchFlush,
             view_name='flush')

register_url(prefix=command_prefix, name=command_name,
             url='/verify/<int:undertaking_id>/<int:oldcompany_id>',
             view=MatchVerify,
             view_name='verify')

register_url(prefix=command_prefix, name=command_name,
             url='/unverify/<int:undertaking_external_id>',
             view=MatchUnverify,
             view_name='unverify')

register_url(prefix=command_prefix, name=command_name,
             url='/test/<new>/<old>',
             view=MatchTest,
             view_name='test')

register_url(prefix=command_prefix, name=command_name,
             url='/manual/<int:undertaking_id>/<oldcompany_account>',
             view=MatchManual,
             view_name='manual')
