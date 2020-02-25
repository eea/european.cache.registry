from flask import current_app

from .undertakings import remove_undertaking
from instance.settings import FGAS


def eea_double_check_fgases(data):
    ok = True

    if not data['businessProfile']:
        businessprofile = ''
        ok = False
    else:
        businessprofile = data['businessProfile']['highLevelUses']

    identifier = """
        Organisation ID: {}
        Organisation status: {}
        Organisation highLevelUses: {}
        Organisation types: {}
        Organisation contact persons: {}
        Organisation domain: {}
    """.format(data['id'], data['status'],
            businessprofile, data['types'],
            data['contactPersons'], data['domain'])

    country_type = data['address']['country']['type']
    has_eu_legal_rep = data.get('euLegalRepresentativeCompany')

    if all([country_type == 'NONEU_TYPE', not has_eu_legal_rep]):
        message = 'NONEU_TYPE Companies must have a representative.'
        current_app.logger.warning(message + identifier)
        ok = False

    if not all(('status' in data, data['status'] in ['VALID', 'REVISION'])):
        message = 'Organisation status differs from VALID or REVISION.'
        current_app.logger.warning(message + identifier)
        ok = False

    if not all([l.startswith('FGAS_') for l in data['types']]):
        message = "Organisation types elements don't start with 'FGAS_'"
        current_app.logger.warning(message + identifier)
        ok = False

    if data['businessProfile']:
        if not all([l.startswith('fgas.')
                    for l in data['businessProfile']['highLevelUses']]):
            message = "Organisation highLevelUses elements don't start with 'fgas.'"
            current_app.logger.warning(message + identifier)
            ok = False
    else:
        message = "Organisation has no highLevelUses"
        data['businessProfile'] = {'highLevelUses': []}
        current_app.logger.warning(message + identifier)
        ok = False

    if not data['domain'] == FGAS:
        message = "Organisation domain is not FGAS"
        current_app.logger.warning(message + identifier)
        ok = False
    return ok
