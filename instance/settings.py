# -*- coding: utf-8 -*-

import os

# Turn this off on production
DEBUG = True if os.environ.get('DEBUG', '') in ('True','true') else False

SQLALCHEMY_DATABASE_URI = '{schema}://{user}:{pwd}@{host}/{dbname}'.format(
  schema=os.environ.get('DB_SCHEMA', 'sqlite'),
  user=os.environ.get('DB_USER', ''),
  pwd=os.environ.get('DB_PASS', ''),
  host=os.environ.get('DB_HOST', ''),
  dbname=os.environ.get('DB_NAME', ''))

BASE_URL = os.environ.get('BASE_URL', 'http://localhost')
API_URL = BASE_URL + '/rest/api'
API_USER = os.environ.get('API_USER', '')
API_PASSWORD = os.environ.get('API_PASSWORD', '')
API_TOKEN = os.environ.get('API_TOKEN', '')

BDR_HOST = os.environ.get('BDR_HOST', '')
BDR_API_URL = os.environ.get('BDR_API_URL', BDR_HOST + '/registry/api')
BDR_API_KEY = os.environ.get('BDR_API_KEY', '')

BDR_ENDPOINT_URL = os.environ.get('BDR_ENDPOINT_URL', '')
BDR_ENDPOINT_USER = os.environ.get('BDR_ENDPOINT_USER', '')
BDR_ENDPOINT_PASSWORD = os.environ.get('BDR_ENDPOINT_PASSWORD', '')

BDR_HELP_DESK_MAIL = os.environ.get('BDR_HELP_DESK_MAIL', '')

LOG_FILE = os.environ.get('LOG_FILE', 'log_file.log')

# email server
MAIL_SERVER = os.environ.get('MAIL_SERVER', '')
MAIL_PORT = os.environ.get('MAIL_PORT', '')
MAIL_USE_TLS = True if os.environ.get('MAIL_USE_TLS', '') in ('True','true') else False
MAIL_USE_SSL = True if os.environ.get('MAIL_USE_SSL', '') in ('True','true') else False
MAIL_USERNAME = os.environ.get('MAIL_USERNAME', '')
MAIL_PASSWORD = os.environ.get('MAIL_PASSWORD', '')
MAILS_SENDER_NAME = os.environ.get('MAILS_SENDER_NAME', 'Help Desk')

 # set it to False to disable
HTTPS_VERIFY = True if os.environ.get('HTTPS_VERIFY', '') in ('True','true') else False

# if set to False, only retrieve organisations with 'fgases' obligation
GET_ALL_INTERESTING_OBLIGATIONS = True if os.environ.get('GET_ALL_INTERESTING_OBLIGATIONS', '') in ('True','true') else False

# specify if notifications mails are sent
SEND_MATCHING_MAILS = True if os.environ.get('SEND_MATCHING_MAILS', '') in ('True','true') else False

# fuzzy matching algorithm percent value (how much should old and new be alike). ex: 75
FUZZ_LIMIT = int(os.environ.get('FUZZ_LIMIT', '75'))

try:
    from instance.localsettings import *
except ImportError:
    pass
