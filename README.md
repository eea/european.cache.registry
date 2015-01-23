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

For syncing bdr without SSL verification, set the following switch in settings:

    HTTPS_VERIFY = False

### Matching

Match fgases data with data from bdr registry:

    ./manage.py match run

Flush existing matches:

    ./manage.py match flush

Verify a match:

    ./manage.py verify [undertaking_id] [oldcompany_id]

Remove an unwanted link:

    ./manage.py unverify [undertaking_id]

it returns None if no company was found, False if the company is now
unverified.

Set a switch in `settings.py` if you want companies with no candidates to be
automatically be set as haveing no matching

    AUTO_VERIFY_NEW_COMPANIES = True
