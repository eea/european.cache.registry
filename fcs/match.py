# coding=utf-8
from fuzzywuzzy import fuzz

from sqlalchemy import or_
from sqlalchemy.orm import joinedload
from flask.ext.script import Manager
from flask import current_app

from fcs import models
from fcs.mails import send_match_mail

from fcs.sync.bdr import call_bdr


match_manager = Manager()


def get_fuzz_limit():
    return current_app.config.get('FUZZ_LIMIT', 75)


def str_matches(new, old):
    return new and old and fuzz.ratio(new, old) >= get_fuzz_limit()


def log_match(company_id, verified, user, oldcompany_account=None):
    matching_log = models.MatchingLog(
        company_id=company_id,
        oldcompany_account=oldcompany_account,
        verified=verified,
        user=user,
    )
    models.db.session.add(matching_log)


def get_unverified_companies(domain):
    return (
        models.Undertaking.query
        .filter(or_(models.Undertaking.oldcompany_verified == None,
                    models.Undertaking.oldcompany_verified == False))
        .filter_by(domain=domain)
    )


def get_all_candidates(domain):
    return get_unverified_companies(domain)


def get_candidates(external_id, domain):
    company = (
        models.Undertaking.query.filter_by(
            external_id=external_id,
            domain=domain
        ).first()
    )
    return company


def get_all_non_candidates(domain, vat=None):
    queryset = (
        models.db.session.query(models.Undertaking)
        .options(joinedload(models.Undertaking.address))
        .options(joinedload(models.Undertaking.represent))
        .options(joinedload(models.Undertaking.businessprofile))
        .options(joinedload(models.Undertaking.contact_persons))
        .filter_by(oldcompany_verified=True)
        .filter_by(domain=domain)
    )
    if vat:
        queryset = queryset.filter_by(vat=vat)
    return queryset.all()


def unverify_link(undertaking_id, domain, user):
    u = models.Undertaking.query.filter_by(
        external_id=undertaking_id,
        domain=domain
    ).first()
    if not u or not u.oldcompany_verified:
        return None

    u.oldcompany_verified = False
    u.oldcompany_account = None
    u.oldcompany_extid = None
    u.oldcompany = None
    log_match(undertaking_id, False, user)
    models.db.session.commit()
    return u


def verify_none(undertaking_id, domain, user):
    u = models.Undertaking.query.filter_by(
        external_id=undertaking_id,
        domain=domain
    ).first()

    if not u:
        return None
    if u.oldcompany_verified is True:
        return u
    u.oldcompany = None
    u.oldcompany_verified = True
    u.oldcompany_account = None
    u.oldcompany_extid = None
    if call_bdr(u, old_collection=None):
        log_match(undertaking_id, True, user,
                  oldcompany_account=None)
        models.db.session.commit()
        send_match_mail(match=False, user=user, company_name=u.name,
                        company_id=u.external_id)
    else:
        models.db.session.rollback()
    return u
