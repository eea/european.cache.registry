from flask import current_app

from .undertakings import remove_undertaking
from instance.settings import FGAS


def eea_double_check_fgases(data):
    identifier = """
        Organisation ID: {}
        Organisation status: {}
        Organisation highLevelUses: {}
        Organisation types: {}
        Organisation contact persons: {}
        Organisation domain: {}
    """.format(data['id'], data['status'],
               data['businessProfile']['highLevelUses'], data['types'],
               data['contactPersons'], data['domain'])
    ok = True
    country_type = data['address']['country']['type']
    has_eu_legal_rep = data.get('euLegalRepresentativeCompany')
    manufacturer = 'FGAS_MANUFACTURER_OF_EQUIPMENT_HFCS' in data['types']

    if all([country_type == 'NONEU_TYPE', not has_eu_legal_rep]) and not \
       all([manufacturer, len(data['types']) == 1,
            len(data.get('businessProfile',
                         {'highLevelUses': []})['highLevelUses']) == 0]):
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

    if not all([l.startswith('fgas.')
                for l in data['businessProfile']['highLevelUses']]):
        message = "Organisation highLevelUses elements don't start with 'fgas.'"
        current_app.logger.warning(message + identifier)
        ok = False

    if not data['domain'] == FGAS:
        message = "Organisation domain is not FGAS"
        current_app.logger.warning(message + identifier)
        ok = False

    return ok
