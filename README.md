fgas-cache-server
=================

A middleware between F-Gas Registry and BDR


Usage (testing)
---------------
Initialize database:

    ./manage.py db init

Fetch the latest data from a test server (cron):

    ./manage.py sync test


Get data from the local server (client):

    ./manage.py api test
