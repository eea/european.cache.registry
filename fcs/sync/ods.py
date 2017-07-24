from flask import current_app


def eea_double_check_ods(data):
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

    if not all(('status' in data, data['status'] in ['VALID', 'DISABLED'])):
        message = 'Organisation status differs from VALID or DISABLED.'
        current_app.logger.warning(message + identifier)
        ok = False

    if all([data['status'] == 'DISABLED', len(data['contactPersons']) > 0]):
        message = "Contact Persons available for DISABLED company"
        current_app.logger.warning(message + identifier)
        ok = False

    if not data['domain'] == 'ODS':
        message = "Organisation domain is not ODS"
        current_app.logger.warning(message + identifier)
        ok = False

    return ok
