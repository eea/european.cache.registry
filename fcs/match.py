from datetime import datetime
from flask.ext.script import Manager
from fcs import models

match_manager = Manager()


def has_match(company, old):
    c_name = company['name'].lower()
    o_name = old['name'].lower()
    return (
        c_name and o_name and (
            c_name in o_name or o_name in c_name
        )
    )


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
                oldcompany_id=old['id']).first()
            if not link:
                link = models.OldCompanyLink(
                    undertaking_id=company['id'], oldcompany_id=old['id'],
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

    links = [l.as_dict() for l in models.OldCompanyLink.query.all()]

    from pprint import pprint

    pprint(links)


@match_manager.command
def flush():
    for link in models.OldCompanyLink.query.all():
        models.db.session.delete(link)

    models.db.session.commit()
