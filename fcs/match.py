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


def add_link(company_id, oldcompany_id):
    link = models.OldCompanyLink.query.filter_by(
        undertaking_id=company_id,
        oldcompany_id=oldcompany_id
    ).first() or models.OldCompanyLink(
        undertaking_id=company_id,
        oldcompany_id=oldcompany_id,
        date_added=datetime.now(),
    )
    models.db.session.add(link)
    return link


def get_unverified_companies():
    return (
        models.Undertaking.query
        .filter(or_(models.Undertaking.oldcompany_verified == None,
                    models.Undertaking.oldcompany_verified == False))
    )


def get_oldcompanies_for_matching():
    qs = models.OldCompany.query.filter_by(undertaking=None, valid=True)
    if not current_app.config.get('GET_ALL_INTERESTING_OBLIGATIONS', ''):
        qs = qs.filter_by(obligation='fgases')
    return qs


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


def get_country(country_code):
    cc = country_code.lower()
    if cc == 'gb':
        cc = 'uk'
    elif cc == 'el':
        cc = 'gr'
    return cc


def has_match(company, old):
    c_code = get_country(company['country_code'])
    o_code = get_country(old['country_code'])
    if c_code != o_code:
        return False

    c_vat = company['vat'] or ''
    o_vat = old['vat_number'] or ''
    if all((c_vat, o_vat)) and c_vat == o_vat:
        return True

    c_name = company['name'].lower()
    o_name = old['name'].lower()
    return str_matches(c_name, o_name)


def get_fuzz_limit():
    return current_app.config.get('FUZZ_LIMIT', 75)


def str_matches(new, old):
    return new and old and fuzz.ratio(new, old) >= get_fuzz_limit()


def match_all(companies, oldcompanies):
    links = []
    new_companies = []

    companies = [c.as_dict() for c in companies]
    oldcompanies = [o.as_dict() for o in oldcompanies]

    for c in companies:
        candidates = [o for o in oldcompanies if has_match(c, o)]
        if candidates:
            links.append((c, candidates))
        else:
            new_companies.append(c)

    for company, candidates in links:
        for old in candidates:
            add_link(company['id'], old['id'])

    models.db.session.commit()
    return links, new_companies


@match_manager.command
def run():
    companies = get_unverified_companies()
    oldcompanies = get_oldcompanies_for_matching()

    links, new_companies = match_all(companies, oldcompanies)
    print len(links), "matching links"
    if current_app.config.get('AUTO_VERIFY_NEW_COMPANIES'):
        print "Autoverifying companies without candidates"
        for c in new_companies:
            verify_none(c['company_id'], 'SYSTEM')
    return True


@match_manager.command
def verify(undertaking_id, oldcompany_id):
    result = verify_link(undertaking_id, oldcompany_id, "None - Mgmt Command")
    if result:
        print result.verified
    else:
        print "No such link"
    return True


@match_manager.command
def flush():
    """ Remove all previously created links in the match database.
    """
    for link in models.OldCompanyLink.query.all():
        models.db.session.delete(link)

    models.db.session.commit()
    return True


@match_manager.command
def unverify(undertaking_external_id):
    """ Remove a link from the matching database """
    u = unverify_link(undertaking_external_id, 'SYSTEM')
    print u and u.oldcompany_verified
    return True


@match_manager.command
def test(new, old):
    """ Show fuzzy match for two words
    """
    print "'{}' and '{}' match by {} (LIMIT: {})".format(new, old,
                                                         fuzz.ratio(new, old),
                                                         get_fuzz_limit())
    return True


@match_manager.command
def manual(undertaking_id, oldcompany_account):
    print "Verifying company: {} with old company account: {}".format(
        undertaking_id, oldcompany_account)
    print verify_manual(undertaking_id, oldcompany_account, 'SYSTEM')
    return True
