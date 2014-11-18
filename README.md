fgas-cache-server
=================

A middleware between F-Gas Registry and BDR


Usage (testing)
---------------
Initialize database:

    ./manage.py db init

Fetch the latest data from a test server (cron):

    ./manage.py sync test_fgases
    ./manage.py sync test_bdr


Get data from the local server (client):

    ./manage.py api test


Match fgases data with data from bdr registry:

    ./manage.py match test

Flush existing matches:

    ./manage.py match flush
