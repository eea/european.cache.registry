from flask import current_app

from .undertakings import remove_undertaking


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

    manufacturer = 'FGAS_MANUFACTURER_OF_EQUIPMENT_HFCS' in data['types']
    if all([manufacturer, len(data['types']) == 1,
            data['address']['country']['type'] == 'NONEU_TYPE']):
        message = 'NONEU_TYPE Equipment manufacturers only, have no reporting'\
                  ' obligations'
        current_app.logger.warning(message + identifier)
        remove_undertaking(data)
        ok = False

    if not all(('status' in data, data['status'] in ['VALID', 'DISABLED'])):
        message = 'Organisation status differs from VALID or DISABLED.'
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

    if all([data['status'] == 'DISABLED', len(data['contactPersons']) > 0]):
        message = "Contact Persons available for DISABLED company"
        current_app.logger.warning(message + identifier)
        ok = False

    if not data['domain'] == 'FGAS':
        message = "Organisation domain is not FGAS"
        current_app.logger.warning(message + identifier)
        ok = False

    return ok
