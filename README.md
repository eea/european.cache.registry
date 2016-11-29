fgas-cache-server
=================

A middleware between F-Gas Registry and BDR


Usage (testing)
---------------

### Database

Initialize database:

    ./manage.py db init

### Sync

Fetch the latest data from a test server (cron):

    ./manage.py sync fgases [-d 30]

In order to sync BDR collections title with the cache server's corresponding undertakings name:

    ./manage.py sync sync_collections_title

For syncing bdr without SSL verification, set the following switch in settings:

    HTTPS_VERIFY = False

For patching the company data, set `PATCH_COMPANIES` to a dictionary
containing values to be updated. Use the company external id as a key.

For patching user access, set `PATCH_USERS` to a list of users to be added to
a company. Use the company external id as a key.

### Matching

Modify the fuzzy matching algorithm percent value (how much should old and new
be alike):

    FUZZ_LIMIT = 75
