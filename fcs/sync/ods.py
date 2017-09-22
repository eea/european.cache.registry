from flask import current_app
from instance.settings import ODS

from fcs.models import Type, BusinessProfile


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

    required_fields = ['@type', 'id', 'name', 'address', 'phone', 'domain',
                       'contactPersons', 'dateCreated', 'dateUpdated',
                       'status', 'eoriNumber', 'types',
                       'businessProfile']
    required_fields_country = ['code', 'name', 'type']
    required_fields_user = ['userName', 'firstName', 'lastName',
                            'emailAddress']
    ok = True
    for field in required_fields:
        if not all((field in data, data[field])):
            message = "Organisation {0} field is missing.".format(field)
            current_app.logger.error(message + identifier)
            ok = False

    if data['@type'] != 'ODSUndertaking':
        message = "Organisation type is not ODSUndertaking."
        current_app.logger.error(message + identifier)
        ok = False

    if not data['domain'] == ODS:
        message = "Organisation domain is not ODS."
        current_app.logger.error(message + identifier)
        ok = False

    if not data['status'] in ['VALID', 'DISABLED']:
        message = 'Organisation status differs from VALID or DISABLED.'
        current_app.logger.error(message + identifier)
        ok = False

    if all([data['status'] == 'DISABLED', len(data['contactPersons']) > 0]):
        message = "Contact Persons available for DISABLED company."
        current_app.logger.error(message + identifier)
        ok = False

    if not all(('country' in data['address'], data['address']['country'])):
        message = 'Organisation address country is missing.'
        current_app.logger.error(message + identifier)
        ok = False

    country = data['address']['country']
    for field in required_fields_country:
        if not all((field in country, country[field])):
            message = "Organisation country {0} is missing.".format(field)
            current_app.logger.error(message + identifier)
            ok = False

    if country['type'] != 'EU_TYPE':
        message = "Organisation country type is not EU_TYPE."
        current_app.logger.error(message + identifier)
        ok = False

    for user in data['contactPersons']:
        for field in required_fields_user:
            if not all((field in user, user[field])):
                message = "Organisation user {0} is missing.".format(field)
                current_app.logger.error(message + identifier)
                ok = False

    types = [object.type for object in Type.query.filter_by(domain=ODS)]
    for type in data['types']:
        if type not in types:
            message = "Organisation type {0} is not accepted.".format(type)
            current_app.logger.error(message + identifier)
            ok = False

    businessprofiles = [object.highleveluses for object in
                        BusinessProfile.query.filter_by(domain=ODS)]
    for high_level_use in data['businessProfile']['highLevelUses']:
        if high_level_use not in businessprofiles:
            message = "Organisation highlevel use {0} is not accepted.".format(
                high_level_use
            )
            current_app.logger.error(message + identifier)
            ok = False

    return ok
