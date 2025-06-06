# coding=utf-8
from flask import Blueprint
from flask.cli import AppGroup

from .auditor import (
    AuditorAssignView,
    AuditorUnassignView,
    AuditorCheckView,
    AuditorDetailView,
    AuditorListView,
    AuditorVerificationEnvelopesView,
)

from .candidate import (
    CandidateList,
    NonCandidateList,
    CandidateVerifyMatchingIds,
    CandidateVerify,
    CandidateVerifyNone,
    CandidateUnverify,
    CandidateVerifyManual,
)
from .commands import (
    SyncAuditorsView,
    SyncCollectionsTitleView,
    SyncFgasesView,
    SyncStocksView,
    MatchFlush,
    SyncODSView,
    SyncLicencesView,
    SyncBdr,
    SyncFgasesDebugNoneuView,
    MatchRun,
)
from .licence import (
    SubstanceYearListView,
    SubstanceListView,
    LicencesOfOneDeliveryListView,
    SubstancesOfOneDeliveryListView,
    ProcessAgentUseView,
)
from .old_company import (
    OldCompanyListValid,
    OldCompanyListInvalid,
    OldCompanySetValid,
    OldCompanySetInvalid,
)
from .stocks import (
    StockListing,
    StocksUndertakingListView,
    StocksYearListView,
    LoadStocksJson,
)
from .undertaking import (
    UndertakingListView,
    UndertakingListSmallView,
    UndertakingListAllView,
    UndertakingListByVatView,
    UndertakingFilterCountView,
    UndertakingDetailView,
    UndertakingDetailShortView,
    UndertakingStatusUpdate,
)
from .user import (
    UserListView,
    UserCompaniesView,
    UserCompaniesIncludeEcasView,
    UserCompaniesAuditorsView,
)

api = Blueprint("api", __name__)
api_manager = AppGroup("api")


def register_url(prefix, url, view, name, view_name):
    api.add_url_rule(rule=prefix + url, view_func=view.as_view(name + "-" + view_name))


# Auditor

auditor_prefix = "/auditors"
auditor_name = "auditor"

register_url(
    prefix=auditor_prefix,
    name=auditor_name,
    url="/list/",
    view=AuditorListView,
    view_name="list",
)

register_url(
    prefix=auditor_prefix,
    name=auditor_name,
    url="/<pk>/details/",
    view=AuditorDetailView,
    view_name="detail",
)

register_url(
    prefix=auditor_prefix,
    name=auditor_name,
    url="/verification_envelopes/",
    view=AuditorVerificationEnvelopesView,
    view_name="verification_envelopes",
)

# Undertaking

undertaking_prefix = "/undertaking/<domain>"
undertaking_name = "company"

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/list",
    view=UndertakingListView,
    view_name="list",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/list-small",
    view=UndertakingListSmallView,
    view_name="list-small",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/list/all",
    view=UndertakingListAllView,
    view_name="list-all",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/list_by_vat/<vat>",
    view=UndertakingListByVatView,
    view_name="list-by-vat",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/filter",
    view=UndertakingFilterCountView,
    view_name="filter",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<pk>/details",
    view=UndertakingDetailView,
    view_name="detail",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<pk>/details-short/",
    view=UndertakingDetailShortView,
    view_name="detail_short",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<pk>/statusupdate",
    view=UndertakingStatusUpdate,
    view_name="statusupdate",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<external_id>/auditor/<auditor_uid>/check",
    view=AuditorCheckView,
    view_name="auditor_check",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<external_id>/auditor/<auditor_uid>/assign/",
    view=AuditorAssignView,
    view_name="auditor_assign",
)

register_url(
    prefix=undertaking_prefix,
    name=undertaking_name,
    url="/<external_id>/auditor/<auditor_uid>/unassign/",
    view=AuditorUnassignView,
    view_name="auditor_unassign",
)

# Licence

licence_prefix = "/undertaking/<domain>/<pk>"
licence_name = "licence"

register_url(
    prefix=licence_prefix,
    name=licence_name,
    url="/licences/<year>/aggregated",
    view=SubstanceYearListView,
    view_name="current_substances_per_undertaking",
)

register_url(
    prefix=licence_prefix,
    name=licence_name,
    url="/licences/aggregated",
    view=SubstanceListView,
    view_name="all_substances_per_undertaking",
)

register_url(
    prefix=licence_prefix,
    name=licence_name,
    url="/<year>/licences",
    view=LicencesOfOneDeliveryListView,
    view_name="licences_per_delivery",
)

register_url(
    prefix=licence_prefix,
    name=licence_name,
    url="/<year>/substances",
    view=SubstancesOfOneDeliveryListView,
    view_name="substances_per_delivery",
)

register_url(
    prefix=licence_prefix,
    name="pau",
    url="/pau",
    view=ProcessAgentUseView,
    view_name="process_agent_use",
)

# Stock
stock_prefix = "/stocks"
stock_name = "stock"
register_url(
    prefix=stock_prefix,
    name=stock_name,
    url="",
    view=StockListing,
    view_name="stock_listing",
)

register_url(
    prefix=stock_prefix,
    name=stock_name,
    url="/<external_id>",
    view=StocksUndertakingListView,
    view_name="undertaking_stocks",
)

register_url(
    prefix=stock_prefix,
    name=stock_name,
    url="/years/<year>",
    view=StocksYearListView,
    view_name="year_stocks",
)

register_url(
    prefix=stock_prefix,
    name=stock_name,
    url="/import",
    view=LoadStocksJson,
    view_name="import_stocks",
)
# User

user_prefix = "/user"
user_name = "user"

register_url(
    prefix=user_prefix, name=user_name, url="/list", view=UserListView, view_name="list"
)

register_url(
    prefix=user_prefix,
    name=user_name,
    url="/<pk>/companies",
    view=UserCompaniesView,
    view_name="companies",
)

register_url(
    prefix=user_prefix,
    name=user_name,
    url="/companies",
    view=UserCompaniesIncludeEcasView,
    view_name="companies_ecas",
)

register_url(
    prefix=user_prefix,
    name=user_name,
    url="/companies/v2/",
    view=UserCompaniesAuditorsView,
    view_name="companies_auditors",
)

# Candidate

candidate_prefix = "/candidate/<domain>"
candidate_name = "candidate"

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/list",
    view=CandidateList,
    view_name="list",
)

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/list/verified",
    view=NonCandidateList,
    view_name="non-list",
)

register_url(
    prefix="/candidate",
    name=candidate_name,
    url="/verify-matching-ids/<undertaking_id>/<oldcompany_id>",
    view=CandidateVerifyMatchingIds,
    view_name="verify-matching-ids",
)

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/verify/<undertaking_id>/<oldcompany_id>",
    view=CandidateVerify,
    view_name="verify",
)

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/verify-none/<undertaking_id>",
    view=CandidateVerifyNone,
    view_name="verify-none",
)

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/unverify/<undertaking_id>/",
    view=CandidateUnverify,
    view_name="unverify",
)

register_url(
    prefix=candidate_prefix,
    name=candidate_name,
    url="/manual/<undertaking_id>/<oldcompany_account>",
    view=CandidateVerifyManual,
    view_name="manual",
)


# Commands

command_prefix = "/sync"
command_name = "sync"

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/auditors/",
    view=SyncAuditorsView,
    view_name="auditors",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/collections_title",
    view=SyncCollectionsTitleView,
    view_name="collections",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/fgases",
    view=SyncFgasesView,
    view_name="fgases",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/ods",
    view=SyncODSView,
    view_name="ods",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/bdr",
    view=SyncBdr,
    view_name="sync-bdr",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/licences",
    view=SyncLicencesView,
    view_name="sync-licences",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/stocks",
    view=SyncStocksView,
    view_name="stocks",
)


register_url(
    prefix=command_prefix,
    name=command_name,
    url="/fgases_debug_noneu",
    view=SyncFgasesDebugNoneuView,
    view_name="fgases-debug-noneu",
)

# Old companies
command_prefix = "/oldcompanies"
command_name = "oldcompany"

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/list/valid/",
    view=OldCompanyListValid,
    view_name="list-valid",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/list/invalid/",
    view=OldCompanyListInvalid,
    view_name="list-invalid",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/<pk>/valid/",
    view=OldCompanySetValid,
    view_name="set-valid",
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/<pk>/invalid/",
    view=OldCompanySetInvalid,
    view_name="set-invalid",
)

# Match
command_prefix = "/match"
command_name = "match"

register_url(
    prefix=command_prefix, name=command_name, url="/run", view=MatchRun, view_name="run"
)

register_url(
    prefix=command_prefix,
    name=command_name,
    url="/flush",
    view=MatchFlush,
    view_name="flush",
)
