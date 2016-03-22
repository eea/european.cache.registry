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
    ./manage.py sync bdr

In order to sync BDR collections title with the cache server's corresponding undertakings name:

    ./manage.py sync sync_collections_title

For syncing bdr without SSL verification, set the following switch in settings:

    HTTPS_VERIFY = False

For patching the company data, set `PATCH_COMPANIES` to a dictionary
containing values to be updated. Use the company external id as a key.

For patching user access, set `PATCH_USERS` to a list of users to be added to
a company. Use the company external id as a key.

### Matching

Match fgases data with data from bdr registry:

    ./manage.py match run

Flush existing matches:

    ./manage.py match flush

Verify a match:

    ./manage.py match verify [undertaking_id] [oldcompany_id]

Verify a manual match:

    ./manage.py match manual [undertaking_id] [oldcompany_account]

Remove an unwanted link:

    ./manage.py match unverify [undertaking_id]

it returns None if no company was found, False if the company is now
unverified.

Set a switch in `settings.py` if you want companies with no candidates to be
automatically be set as haveing no matching

    AUTO_VERIFY_NEW_COMPANIES = True

Set a switch in `settings.py` if you want to match companies within all
obligations from BDR Registry:

    GET_ALL_INTERESTING_OBLIGATIONS = False

Modify the fuzzy matching algorithm percent value (how much should old and new
be alike):

    FUZZ_LIMIT = 75
