# European Cache Registry

[![Travis](https://travis-ci.org/eea/european.cache.registry.svg?branch=master)](
https://travis-ci.org/eea/european.cache.registry)
[![Coverage](https://coveralls.io/repos/github/eea/european.cache.registry/badge.svg?branch=master)](
https://coveralls.io/github/eea/european.cache.registry)
[![Docker build](https://img.shields.io/docker/automated/eeacms/european.cache.registry)](https://hub.docker.com/r/eeacms/european.cache.registry)
[![Docker latest version](https://img.shields.io/docker/v/eeacms/european.cache.registry)]()


A middleware between FGAS and ODS Registries and BDR.

This application fetches data from FGAS/ODS and BDR, runs a fuzzy matching algorithm
between the new companies (called Undertakings) that were imported from the
specific registries and the old companies (called Companies) that used BDR for reporting
before switching to FGAS/ODS registries.

Matching is a two-step process, since the fuzzy matching algorithm results have to be
verified by a authenticated user.

* A matching **command** is run which creates link objects for matching Undertaking - Company pairs - this command can also be configured to verify all undertakings from a domain or undertakings for which the algorithm cannot find a match.
* An authenticated user can **verify** the link created by the matching algorithm. If a mistake was made, the link can be unverified.
* An authenticated user can make a **manual** connection between an Undertaking and a Company, without a prior matching link.

## Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

## Installing the application

1. Clone the repository:

        git clone https://github.com/eea/european.cache.registry
        cd european.cache.registry

1. Customize env files:

        cp .secret.example .secret
        vim .secret
        cp docker/init.sql.example docker/init.sql
        vim docker/init.sql

    *NOTE: You will need to manually add the values to `.secret` in order to be
    able to run and use the application locally.*

1. Start application stack:

        docker-compose pull
        docker-compose up -d
        docker-compose logs

1. Attach to the container:

        docker exec -it ecr.app sh

1. Run the tests:

        py.test --cov=cache_registry testsuite

1. Run the server:

        python -m flask run -h 0.0.0.0 -p 5000

1. On Postman, you can access the application at http://localhost:5000, using
the following header:

        Authorization: <token>

    Where `<token>` is the value of the `API_TOKEN` variable in the `.secret`
    file.

## Upgrading the application

1. Get the latest version of source code:

        cd european.cache.registry
        git pull origin master

1. Update the application stack, all services should be "Up":

        docker-compose up -d
        docker-compose ps

## Development instructions

1. Customize docker orchestration for local development:

        cp docker-compose.override.dev.yml docker-compose.override.yml

By default, it builds a local image for app service and maps the project directory
inside the app container.

You can add a fixed port number instead the floating one by specifying it under
the ports directive (e.g. "5000:5000" instead of "5000").

1. Start stack, all services should be "Up" :

        docker-compose up -d
        docker-compose ps

1. Check application logs:

        docker-compose logs

1. When the image is modified you should update the stack:

        docker-compose down -v #optional step for droping all containers and volumes
        docker-compose up -d --build

## Data import

* Copy the test database in ecr.db container and import into postgres:

        docker cp ecr.sql ecr.db:ecr.sql
        docker exec -it ecr.db bash
        psql ecr -U ecr < ecr.sql

## Syncronise with FGAS/ODS Portal

* Fetch the latest data from a test server:

        python -m flask sync fgases [-d 30]
        python -m flask sync ods [-d 30]


* In order to sync from a long time ago, it is advised to use pagination. To use pagination, you must give -p parameter, containing the
* number of companies that are brought in one request.

        python -m flask sync fgases [-d 30] [-p 100]
        python -m flask sync ods [-d 30] [-p 100]

* Fetch a specific company by providing the external id:

        python -m flask sync fgases [-i 12345]
        python -m flask sync ods [-i 12345]


* In order to sync BDR collections title with the cache server's corresponding undertakings name:

        python -m flask sync sync_collections_title

* For syncing bdr without SSL verification, set the following switch in settings:

        HTTPS_VERIFY = False

For patching the company data, set `PATCH_COMPANIES` to a dictionary
containing values to be updated. Use the company external id as a key.

For patching user access, set `PATCH_USERS` to a list of users to be added to
a company. Use the company external id as a key.

For patching licences, set `PATCH_LICENCES` to a list of licences to be added to
a licences/aggregated endpoint. Only the data for the company_id and the given year will
be patched.

## Syncronise with Licence Portal

* The licences for ODS are now taken from DG Clima and exposed:
        python -m flask sync licences 2017 2017-1
        python -m flask sync licences 2017 2017-1

* The first parameter [2017], represents the year from which those deliveries are taken.
* The second parameter [2017-1], represents the name of the delivery.

* The licences are taken for each company. When a new delivery arrives, all old deliveries of the company are moved to
the history object that contains that delivery and for that company.

### Matching

* Modify the fuzzy matching algorithm percent value (how much should old and new be alike):

        FUZZ_LIMIT = 75

* List domains, separated by commas, on which matching should be run:

        MANUAL_VERIFY_ALL_COMPANIES = ODS,FGAS

* List domains, separated by commas, on which matching shouldn't be run

        AUTO_VERIFY_ALL_COMPANIES = FGAS

* Specify if on companies with a certain domain and no match found
by the algorithm should be auto-verified(!This company should also be declared in MANUAL_VERIFY_ALL_COMPANIES):

        AUTO_VERIFY_NEW_COMPANIES = FGAS,ODS

**! Make sure you don't leave a space between the domains (FGAS,ODS not ~~FGAS, ODS~~)**

* Run matching algorithm:

        docker exec ecr.app bash -c "python -m flask match run"

* Cleanup all existing links made by the matching command, verified or not:

        docker exec ecr.app bash -c "python -m flask flush"

* Verify link made by the matching algorithm:

        docker exec ecr.app bash -c
            "python -m flask verify {undertaking_id} {oldcompany_id}"

* Unverify link made by the matching algorithm and already verified:

        docker exec ecr.app bash -c
            "python -m flask unverify {undertaking_id} {domain}"

* Manually connect undertaking and old company on a certain domain, without creating a matching link like the algorithm does:

        docker exec ecr.app bash -c
            "python -m flask manual {undertaking_id} {domain} {oldcompany_id}"

## Testing

1. Run tests:

        docker exec -it ecr.app sh
        py.test --cov=cache_registry testsuite

1. Generate a coverage report:

        py.test --cov-report html --cov=cache_registry testsuite
