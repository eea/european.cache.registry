from fuzzywuzzy import fuzz
from datetime import datetime
from flask.ext.script import Manager
from fcs import models

FUZZ_LIMIT = 80

match_manager = Manager()


def get_all_candidates():
    companies = models.Undertaking.query.filter_by(oldcompany=None)
    data = [(company, company.links) for company in companies if company.links]
    return data


def get_candidates(external_id):
    companies = models.Undertaking.query.filter_by(external_id=external_id)
    data = companies.first().links if companies else []
    return data


def get_all_non_candidates():
    companies = (models.Undertaking.query
                 .filter(models.Undertaking.oldcompany is not None))
    data = companies.all()
    return data


def verify_link(undertaking_id, oldcompany_id):
    link = (
        models.OldCompanyLink.query
        .filter_by(undertaking_id=undertaking_id,
                   oldcompany_id=oldcompany_id).first()
    )
    if link:
        link.verified = True
        link.date_verified = datetime.now()
        link.undertaking.oldcompany = link.oldcompany
        models.db.session.commit()
    return link


def unverify_link(undertaking_id):
    u = models.Undertaking.query.get(undertaking_id)
    if u.oldcompany:
        link = (
            models.OldCompanyLink.query
            .filter_by(undertaking_id=undertaking_id,
                       oldcompany_id=u.oldcompany_id).first()
        )
        if link:
            link.verified = False
            link.date_verified = None

        u.oldcompany = None
        models.db.session.commit()


def has_match(company, old):
    c_code = company['country_code'].lower()
    o_code = company['country_code'].lower()
    if c_code != o_code:
        return False

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
def test():
    companies = models.Undertaking.query.filter_by(oldcompany=None)
    oldcompanies = models.OldCompany.query.filter_by(undertaking=None)

    match_all(companies, oldcompanies)
    models.db.session.commit()

    for company, links in get_all_candidates():
        print u"[{}] {}:".format(company.id, company.name)
        for l in links:
            print u" - [{}] {} {}".format(l.oldcompany_id, l.oldcompany.name,
                                          l.verified)


@match_manager.command
def verify(undertaking_id, oldcompany_id):
    result = verify_link(undertaking_id, oldcompany_id)
    if result:
        print result.verified
    else:
        print "No such link"


@match_manager.command
def flush():
    for link in models.OldCompanyLink.query.all():
        models.db.session.delete(link)

    models.db.session.commit()
