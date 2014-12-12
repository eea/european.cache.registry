import requests

from fuzzywuzzy import fuzz
from datetime import datetime
from sqlalchemy import or_

from flask.ext.script import Manager
from flask import current_app

from fcs import models

FUZZ_LIMIT = 80

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
    models.db.session.commit()


def get_auth():
    return (
        current_app.config.get('BDR_ENDPOINT_USER', 'user'),
        current_app.config.get('BDR_ENDPOINT_PASSWORD', 'pass'),
    )


def get_absolute_url(url):
    return current_app.config['BDR_ENDPOINT_URL'] + url


def do_bdr_request(params):
    url = get_absolute_url('/ReportekEngine/update_company_collection')
    auth = get_auth()
    ssl_verify = current_app.config['HTTPS_VERIFY']
    response = requests.get(url, params=params, auth=auth, verify=ssl_verify)
    return response


def get_eu_country_code(undertaking):
    if undertaking.address.country.type == 'EU_TYPE':
        return undertaking.country_code
    return undertaking.represent.address.country.code


def get_all_candidates():
    companies = (
        models.Undertaking.query
        .filter(or_(models.Undertaking.oldcompany_verified == None,
                    models.Undertaking.oldcompany_verified == False))
    )
    data = [(company, company.links) for company in companies]
    return data


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
    if link:
        link.verified = True
        link.date_verified = datetime.now()
        link.undertaking.oldcompany = link.oldcompany
        link.undertaking.oldcompany_account = link.oldcompany.account
        link.undertaking.oldcompany_verified = True
        link.undertaking.oldcompany_extid = link.oldcompany.external_id
        models.db.session.commit()
        params = {
            'company_id': undertaking_id,
            'domain': undertaking.domain,
            'country': get_eu_country_code(undertaking),
            'name': undertaking.name,
            'old_collection_id': undertaking.oldcompany_account,
        }
        response = do_bdr_request(params)
        log_match(undertaking_id, oldcompany_id, True, user,
                  oldcompany_account=undertaking.oldcompany_account)
    return link


def unverify_link(undertaking_id, user):
    u = models.Undertaking.query.filter_by(external_id=undertaking_id).first()
    if u and u.oldcompany_verified:
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
        models.db.session.commit()
        log_match(undertaking_id, None, False, user)
    return u


def verify_none(undertaking_id, user):
    u = models.Undertaking.query.filter_by(external_id=undertaking_id).first()
    if u:
        u.oldcompany = None
        u.oldcompany_verified = True
        u.oldcompany_account = None
        u.oldcompany_extid = None
        models.db.session.commit()
        params = {
            'company_id': undertaking_id,
            'domain': u.domain,
            'country': get_eu_country_code(u),
            'name': u.name,
        }
        response = do_bdr_request(params)
        log_match(undertaking_id, None, True, user)
    return u


def has_match(company, old):
    c_code = company['country_code'].lower()
    o_code = old['country_code'].lower()
    if c_code != o_code:
        return False

    c_vat = company['vat'] or ''
    o_vat = old['vat_number'] or ''
    if all((c_vat, o_vat)) and c_vat == o_vat:
        return True

    c_name = company['name'].lower()
    o_name = old['name'].lower()
    return all((c_name, o_name)) and fuzz.ratio(c_name, o_name) >= FUZZ_LIMIT


def match_all(companies, oldcompanies):
    links = []

    companies = [c.as_dict() for c in companies]
    oldcompanies = [o.as_dict() for o in oldcompanies]

    for c in companies:
        candidates = [o for o in oldcompanies if has_match(c, o)]
        if candidates:
            links.append((c, candidates))

    for company, candidates in links:
        for old in candidates:
            link = models.OldCompanyLink.query.filter_by(
                undertaking_id=company['id'],
                oldcompany_id=old['id']
            ).first()
            if not link:
                link = models.OldCompanyLink(
                    undertaking_id=company['id'],
                    oldcompany_id=old['id'],
                    date_added=datetime.now(),
                )
                models.db.session.add(link)
    return links


@match_manager.command
def run():
    companies = models.Undertaking.query.filter_by(oldcompany=None)
    oldcompanies = models.OldCompany.query.filter_by(undertaking=None)

    match_all(companies, oldcompanies)
    models.db.session.commit()

    for company, links in get_all_candidates():
        print u"[{}] {} - {}:".format(company.id, company.name,
                                      company.country_code)
        for l in links:
            print u" - [{}] {} {} - {}".format(l.oldcompany_id,
                                               l.oldcompany.name,
                                               l.verified,
                                               l.oldcompany.country_code)


@match_manager.command
def verify(undertaking_id, oldcompany_id):
    result = verify_link(undertaking_id, oldcompany_id, "None - Mgmt Command")
    if result:
        print result.verified
    else:
        print "No such link"


@match_manager.command
def flush():
    for link in models.OldCompanyLink.query.all():
        models.db.session.delete(link)

    models.db.session.commit()
