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


### Matching

Match fgases data with data from bdr registry:

    ./manage.py match run

Flush existing matches:

    ./manage.py match flush

Verify a match:

    ./manage.py verify [undertaking_id] [oldcompany_id]
