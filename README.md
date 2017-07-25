fgas-cache-server
=================

A middleware between F-Gas and ODS Registries and BDR


Installation
------------

* Install `Docker <https://docker.com>`_
* Install `Docker Compose <https://docs.docker.com/compose>`_

Usage
-----

1. Clone the repository:

        $ git clone https://github.com/eea/eea.docker.fcs
        $ cd eea.docker.fcs

2. Customize env files:

        $ cp .secret.example .secret
        $ vim .secret

3. Start application stack:

        $ docker-compose pull
        $ docker-compose up -d
        $ docker-compose logs

4. Create a superuser:

        $ docker exec -it fcs.app sh
        $ ./manage.py createsuperuser

5. Run tests:

        $ docker exec -it fcs.app sh
        # apk add --no-cache libxslt-dev libffi-dev
        # pip install -r requirements-dev.txt
        # ./manage.py test
        # py.test --cov=fcs testsuite

6. Type: http://localhost:8000


Data import
-----------

Copy the test database in fcs.db container and import into mysql:

    $ docker cp fcs.sql fcs.db:/var/lib/mysql/fcs.sql
    $ docker exec -it fcs.db bash
    # mysql -uroot -p fcs < /var/lib/mysql/fcs.sql

Syncronise with FGAS/ODS Portal
--------------------------------

Fetch the latest data from a test server:

    $ docker exec fcs.app bash -c "python ./manage.py sync fgases -d 500"

    ./manage.py sync fgases [-d 30]
    ./manage.py sync ods [-d 30]

In order to sync BDR collections title with the cache server's corresponding undertakings name:

    $ docker exec fcs.app bash -c "./manage.py sync sync_collections_title"

For syncing bdr without SSL verification, set the following switch in settings:

    HTTPS_VERIFY = False

For patching the company data, set `PATCH_COMPANIES` to a dictionary
containing values to be updated. Use the company external id as a key.

For patching user access, set `PATCH_USERS` to a list of users to be added to
a company. Use the company external id as a key.

Matching
--------

Modify the fuzzy matching algorithm percent value (how much should old and new
be alike):

    FUZZ_LIMIT = 75

### DEBUGING

Fetch the latest data from a test server (cron) and prints the list of NON EU companies
without a legal representative:

    $ docker exec fcs.app bash -c "python ./manage.py sync fgases_debug_noneu -d 500"

    ./manage.py sync fgases_debug_noneu [-d 30]
    ./manage.py sync ods_debug_noneu [-d 30]

### Testing

    pip install -r requirements-dev.txt
    py.test --cov=fcs testsuite

Generate a coverage report:

    py.test --cov-report html --cov=fcs testsuite