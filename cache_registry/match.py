# coding=utf-8
from datetime import datetime
import click
from fuzzywuzzy import fuzz

from sqlalchemy import or_
from flask.cli import AppGroup

from flask import current_app
from flask.cli import with_appcontext

from cache_registry import models
from cache_registry.mails import send_match_mail

from cache_registry.sync.bdr import call_bdr
from instance.settings import FGAS, ODS
from sqlalchemy.orm import joinedload

match_manager = AppGroup('match')


def get_fuzz_limit():
    return current_app.config.get('FUZZ_LIMIT', 75)


def str_matches(new, old):
    return new and old and fuzz.ratio(new, old) >= get_fuzz_limit()


def log_match(company_id, oldcompany_id, verified, user, domain,
              oldcompany_account=None):
    matching_log = models.MatchingLog(
        company_id=company_id,
        oldcompany_id=oldcompany_id,
        oldcompany_account=oldcompany_account,
        verified=verified,
        user=user,
        domain=domain
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


def get_unverified_companies(domains):
    return (
        models.Undertaking.query
        .filter(or_(models.Undertaking.oldcompany_verified == None,
                    models.Undertaking.oldcompany_verified == False))
        .filter(models.Undertaking.domain.in_(domains))
    )


def get_unverified_non_eu_no_represent_companies():
    return [company for company in
            get_unverified_companies([FGAS]).filter_by(represent_id=None).all()
            if company.address.country.type == 'NONEU_TYPE']


def get_oldcompanies_for_matching():
    qs = models.OldCompany.query.filter_by(undertaking=None, valid=True)
    obligations = current_app.config.get('MANUAL_VERIFY_ALL_COMPANIES',
                                         [ODS])
    qs = qs.filter(models.OldCompany.obligation.in_(obligations))
    return qs


def get_all_candidates(domain):
    companies = get_unverified_companies([domain])
    data = [(company, company.links) for company in
            companies]
    return data


def get_candidates(external_id, domain):
    company = (
        models.Undertaking.query.filter_by(
            external_id=external_id,
            domain=domain
        ).first()
    )
    return company and company.links


def get_all_non_candidates(domain='FGAS', vat=None):

    queryset = (
        models.db.session.query(models.Undertaking)
        .options(joinedload(models.Undertaking.address))
        .options(joinedload(models.Undertaking.represent))
        .options(joinedload(models.Undertaking.represent_history))
        .options(joinedload(models.Undertaking.businessprofiles))
        .options(joinedload(models.Undertaking.contact_persons))
        .options(joinedload(models.Undertaking.types))
        .filter_by(oldcompany_verified=True)
        .filter_by(domain=domain)
    )
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
    commit = True
    if not link.undertaking.check_passed:
        commit = call_bdr(undertaking, old_collection=True)
    if commit:
        log_match(undertaking_id, oldcompany_id, True, user,
                  domain=undertaking.domain,
                  oldcompany_account=undertaking.oldcompany_account
                  )
        models.db.session.commit()
        send_match_mail(match=True, user=user,
                        company_name=undertaking.name,
                        company_id=undertaking.external_id,
                        oldcompany_name=oldcompany.name,
                        domain=undertaking.domain)
    else:
        models.db.session.rollback()

    return link


def unverify_link(undertaking_id, domain, user):
    u = models.Undertaking.query.filter_by(
        external_id=undertaking_id,
        domain=domain
    ).first()
    if not u or not u.oldcompany_verified:
        return None
    link = (
        models.OldCompanyLink.query.filter_by(
            undertaking_id=undertaking_id,
            oldcompany_id=u.oldcompany_id).first()
    )
    if link:
        link.verified = False
        link.date_verified = None

    u.oldcompany_verified = False
    u.oldcompany_account = None
    u.oldcompany_extid = None
    u.oldcompany = None
    log_match(undertaking_id, None, False, user, domain=domain)
    models.db.session.commit()
    return u


def verify_none(undertaking_id, domain, user):
    return verify_manual(undertaking_id, domain, None, user)


def verify_manual(undertaking_id, domain, oldcompany_account, user):
    u = models.Undertaking.query.filter_by(
        external_id=undertaking_id,
        domain=domain.upper()
    ).first()
    if not u:
        return None
    u.oldcompany = None
    u.oldcompany_verified = True
    u.oldcompany_account = oldcompany_account
    u.oldcompany_extid = None
    commit = True
    if not u.check_passed:
        commit = call_bdr(u, old_collection=oldcompany_account)
    if commit:
        log_match(undertaking_id, None, True, user,
                  domain=domain,
                  oldcompany_account=oldcompany_account)
        models.db.session.commit()
        send_match_mail(match=False, user=user, company_name=u.name,
                        company_id=u.external_id, domain=domain)
    else:
        models.db.session.rollback()
    return u


def get_country(country_code):
    if not country_code:
        return
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
    o_vat = old['eori'] or ''
    if all((c_vat, o_vat)) and c_vat == o_vat:
        return True
    c_name = company['name'].lower()
    o_name = old['name'].lower()
    return str_matches(c_name, o_name)


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


@match_manager.command('run')
def run():
    return call_run()

def call_run():
    no_represent_companies = get_unverified_non_eu_no_represent_companies()

    for company in no_represent_companies:
        verify_none(company.external_id, company.domain, 'SYSTEM')

    auto_verify_domains = current_app.config.get(
        'AUTO_VERIFY_ALL_COMPANIES', []
    )
    companies = get_unverified_companies(auto_verify_domains)

    for company in companies:
        verify_none(company.external_id, company.domain, 'SYSTEM')
    interesting_obligations = current_app.config.get(
        'MANUAL_VERIFY_ALL_COMPANIES', [])
    companies = get_unverified_companies(interesting_obligations)
    oldcompanies = get_oldcompanies_for_matching()

    links, new_companies = match_all(companies, oldcompanies)
    print(len(links), "matching links")
    verify_new_companies = current_app.config.get('AUTO_VERIFY_NEW_COMPANIES')
    if verify_new_companies:
        print("Autoverifying companies without candidates")
        for new_company in new_companies:
            if new_company['domain'] in verify_new_companies:
                verify_none(new_company['company_id'], new_company['domain'],
                            'SYSTEM')
    return True


@match_manager.command('verify')
@click.option('-u', '--undertaking_id', 'undertaking_id')
@click.option('-o', '--oldcompany_id', 'oldcompany_id')
def verify(undertaking_id, oldcompany_id):
    result = verify_link(undertaking_id, oldcompany_id, "None  Mgmt Command")
    if result:
        print(result.verified)
    else:
        print("No such link")
    return True


@match_manager.command('flush')
def flush():
    """ Remove all previously created links in the match database."""
    return call_flush()

def call_flush():
    for link in models.OldCompanyLink.query.all():
        models.db.session.delete(link)
    models.db.session.commit()
    return True

@match_manager.command('unverify')
@click.option('-u', '--undertaking_external_id', 'undertaking_external_id')
@click.option('-d', '--domain', 'domain')
def unverify(undertaking_external_id, domain):
    """ Remove a link from the matching database """
    u = unverify_link(undertaking_external_id, domain, 'SYSTEM')
    print(u and u.oldcompany_verified)
    return True


@match_manager.command('test')
def test(new, old):
    """ Show fuzzy match for two words"""
    print("'{}' and '{}' match by {} (LIMIT: {})".format(new, old,
                                                         fuzz.ratio(new, old),
                                                         get_fuzz_limit()))
    return True


@match_manager.command('manual')
@click.option('-u', '--undertaking_id', 'undertaking_id')
@click.option('-d', '--domain', 'domain')
@click.option('-o', '--oldcompany_account', 'oldcompany_account')
def manual(undertaking_id, domain, oldcompany_account):
    print("Verifying company: {} with old company account: {}".format(
        undertaking_id, oldcompany_account))
    print(verify_manual(undertaking_id, domain, oldcompany_account, 'SYSTEM'))
    return True
