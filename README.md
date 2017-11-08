european.cache.registry
=======================

A middleware between FGAS and ODS Registries and BDR.

This application fetches data from FGAS/ODS and BDR, runs a fuzzy matching algorithm
between the new companies (called Undertakings) that were imported from the
specific registries and the old companies (called Companies) that used BDR for reporting
before switching to FGAS/ODS registries.

Matching is a two-step process, since the fuzzy matching algorithm results have to be
verified by a authenticated user.
* A matching **command** is run which creates link objects for matching Undertaking -
Company pairs - this command can also be configured to verify all undertakings from
a domain or undertakings for which the algorithm cannot find a match.
* An authenticated user can **verify** the link created by the matching algorithm. If a
mistake was made, the link can be unverified.
* An authenticated user can make a **manual** connection between an Undertaking and a
Company, without a prior matching link.

[![Travis](https://travis-ci.org/eea/european.cache.registry.svg?branch=master)](
https://travis-ci.org/eea/european.cache.registry)
[![Coverage](https://coveralls.io/repos/github/eea/european.cache.registry/badge.svg?branch=master)](
https://coveralls.io/github/eea/european.cache.registry)

### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installing the application

1. Clone the repository:

        $ git clone https://github.com/eea/european.cache.registry
        $ cd european.cache.registry

2. Customize env files:

        $ cp .secret.example .secret
        $ vim .secret

3. Start application stack:

        $ docker-compose pull
        $ docker-compose up -d
        $ docker-compose logs

4. Run tests:

        $ docker exec -it ecr.app sh
        # pip install -r requirements-dev.txt
        # py.test --cov=cache_registry testsuite

5. Type: http://localhost:5000

### Upgrading the application

1. Get the latest version of source code:

        $ cd european.cache.registry
        $ git pull origin master

2. Update the application stack, all services should be "Up":

        $ docker-compose up -d
        $ docker-compose ps

### Development instructions

1. Customize docker orchestration for local development:
        
        $ cp docker-compose.override.dev.yml docker-compose.override.yml

By default, it builds a local image for app service and maps the project directory
inside the app container.

You can add a fixed port number instead the floating one by specifying it under
the ports directive (e.g. "5000:5000" instead of "5000").

2. Start stack, all services should be "Up" :

        $ docker-compose up -d
        $ docker-compose ps

3. Check application logs:

        $ docker-compose logs

4. When the image is modified you should update the stack:
    
        $ docker-compose down -v #optional step for droping all containers and volumes
        $ docker-compose up -d --build
        
### DEBUGING
* Please make sure that `DEBUG=True` in `.secret`

* Update `docker-compose.override.yml` file `app` section with the following so that
`docker-entrypoint.sh` is not executed:

        entrypoint: ["/usr/bin/tail", "-f", "/dev/null"]
        
* Attach to docker container and start the server in debug mode:
        
        $ docker exec -it ecr.app sh
        # ./manage.py runserver -h 0.0.0.0 -p 5000

### Data import

* Copy the test database in ecr.db container and import into mysql:

        $ docker cp ecr.sql ecr.db:/var/lib/mysql/ecr.sql
        $ docker exec -it ecr.db bash
        # mysql -uroot -p ecr < /var/lib/mysql/ecr.sql

### Syncronise with FGAS/ODS Portal

* Fetch the latest data from a test server:

        $ docker exec ecr.app bash -c "python ./manage.py sync fgases -d 500"
        ./manage.py sync fgases [-d 30]
        ./manage.py sync ods [-d 30]

* In order to sync BDR collections title with the cache server's corresponding undertakings name:

        $ docker exec ecr.app bash -c "./manage.py sync sync_collections_title"

* For syncing bdr without SSL verification, set the following switch in settings:

        HTTPS_VERIFY = False

For patching the company data, set `PATCH_COMPANIES` to a dictionary
containing values to be updated. Use the company external id as a key.

For patching user access, set `PATCH_USERS` to a list of users to be added to
a company. Use the company external id as a key.

### Matching

* Modify the fuzzy matching algorithm percent value (how much should old and new
be alike):

        FUZZ_LIMIT = 75

* List domains, separated by commas, on which matching should be run:
 
        INTERESTING_OBLIGATIONS = ODS

* List domains, separated by commas, on which matching shouldn't be run

        AUTO_VERIFY_ALL_COMPANIES = FGAS

* Specify if companies with no match found by the algorithm should be auto-verified:

        AUTO_VERIFY_NEW_COMPANIES = False

* Run matching algorithm:

        $ docker exec ecr.app bash -c "python ./manage.py run"

* Cleanup all existing links made by the matching command, verified or not:

        $ docker exec ecr.app bash -c "python ./manage.py flush"

* Verify link made by the matching algorithm:

        $ docker exec ecr.app bash -c
            "python ./manage.py verify {undertaking_id} {oldcompany_id}"

* Unverify link made by the matching algorithm and already verified:

        $ docker exec ecr.app bash -c
            "python ./manage.py unverify {undertaking_id} {domain}"

* Manualy connect undertaking and old company on a certain domain, without creating a
matching link like the algorithm does:

        $ docker exec ecr.app bash -c
            "python ./manage.py manual {undertaking_id} {domain} {oldcompany_id}"


### Testing
1. Run tests:

        $ docker exec -it ecr.app sh
        # pip install -r requirements-dev.txt
        # py.test --cov=cache_registry testsuite

* Generate a coverage report:

        py.test --cov-report html --cov=cache_registry testsuite
