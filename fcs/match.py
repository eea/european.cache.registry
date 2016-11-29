# coding=utf-8
from datetime import datetime

from fuzzywuzzy import fuzz

from sqlalchemy import or_
from flask.ext.script import Manager
from flask import current_app

from fcs import models
from fcs.mails import send_match_mail

from fcs.sync.bdr import call_bdr


match_manager = Manager()


def log_match(company_id, oldcompany_id, verified, user,
              oldcompany_account=None):
    matching_log = models.MatchingLog(
        company_id=company_id,
        oldcompany_id=oldcompany_id,
        oldcompany_account=oldcompany_account,
        verified=verified,
        user=user,
    )
    models.db.session.add(matching_log)


def get_unverified_companies():
    return (
        models.Undertaking.query
        .filter(or_(models.Undertaking.oldcompany_verified == None,
                    models.Undertaking.oldcompany_verified == False))
    )


def get_all_candidates():
    return get_unverified_companies()


def get_candidates(external_id):
    company = (
        models.Undertaking.query.filter_by(external_id=external_id).first()
    )
    return company and company.links


def get_all_non_candidates(vat=None):
    queryset = models.Undertaking.query.filter_by(oldcompany_verified=True)
    if vat:
        queryset = queryset.filter_by(vat=vat)
    return queryset.all()


def verify_link(undertaking_id, oldcompany_id, user):
    undertaking = models.Undertaking.query.filter_by(
        external_id=undertaking_id).first()
    oldcompany = models.OldCompany.query.filter_by(
        external_id=oldcompany_id).first()
    link = (
        models.OldCompanyLink.query
        .filter_by(undertaking=undertaking, oldcompany=oldcompany).first()
    )
    if not link:
        return None

    link.verified = True
    link.date_verified = datetime.now()
    link.undertaking.oldcompany = link.oldcompany
    link.undertaking.oldcompany_account = link.oldcompany.account
    link.undertaking.oldcompany_verified = True
    link.undertaking.oldcompany_extid = link.oldcompany.external_id
    if call_bdr(undertaking, old_collection=True):
        log_match(undertaking_id, oldcompany_id, True, user,
                  oldcompany_account=undertaking.oldcompany_account)
        models.db.session.commit()
        send_match_mail(match=True, user=user,
                        company_name=undertaking.name,
                        company_id=undertaking.external_id,
                        oldcompany_name=oldcompany.name)
    else:
        models.db.session.rollback()
    return link


def unverify_link(undertaking_id, user):
    u = models.Undertaking.query.filter_by(external_id=undertaking_id).first()
    if not u or not u.oldcompany_verified:
        return None
    link = (
        models.OldCompanyLink.query
        .filter_by(undertaking_id=undertaking_id,
                   oldcompany_id=u.oldcompany_id).first()
    )
    if link:
        link.verified = False
        link.date_verified = None

    u.oldcompany_verified = False
    u.oldcompany_account = None
    u.oldcompany_extid = None
    u.oldcompany = None
    log_match(undertaking_id, None, False, user)
    models.db.session.commit()
    return u


def verify_none(undertaking_id, user):
    return verify_manual(undertaking_id, None, user)


def verify_manual(undertaking_id, oldcompany_account, user):
    u = models.Undertaking.query.filter_by(external_id=undertaking_id).first()
    if not u:
        return None
    u.oldcompany = None
    u.oldcompany_verified = True
    u.oldcompany_account = oldcompany_account
    u.oldcompany_extid = None
    if call_bdr(u, old_collection=oldcompany_account):
        log_match(undertaking_id, None, True, user,
                  oldcompany_account=oldcompany_account)
        models.db.session.commit()
        send_match_mail(match=False, user=user, company_name=u.name,
                        company_id=u.external_id)
    else:
        models.db.session.rollback()
    return u


def get_fuzz_limit():
    return current_app.config.get('FUZZ_LIMIT', 75)


def str_matches(new, old):
    return new and old and fuzz.ratio(new, old) >= get_fuzz_limit()

