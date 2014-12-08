fgas-cache-server
=================

A middleware between F-Gas Registry and BDR


Usage (testing)
---------------

### Database

Initialize database:

    ./manage.py db init

### API

Fetch the latest data from a test server (cron):

    ./manage.py sync test_fgases [-d 30]
    ./manage.py sync test_bdr

Get data from the local server (client):

    ./manage.py api test


### Matching

Match fgases data with data from bdr registry:

    ./manage.py match test

Flush existing matches:

    ./manage.py match flush

Verify a match:

    ./manage.py verify [undertaking_id] [oldcompany_id]
