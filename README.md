fgas-cache-server
=================

A middleware between F-Gas and ODS Registries and BDR

[![Travis](https://travis-ci.org/eea/eea.docker.fcs.svg?branch=master)](
https://travis-ci.org/eea/eea.docker.fcs)
[![Coverage](https://coveralls.io/repos/github/eea/eea.docker.fcs/badge.svg?branch=master)](
https://coveralls.io/github/eea/eea.docker.fcs)

### Prerequisites

* Install [Docker](https://docs.docker.com/engine/installation/)
* Install [Docker Compose](https://docs.docker.com/compose/install/)

### Installing the application

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

4. Run tests:

        $ docker exec -it fcs.app sh
        # pip install -r requirements-dev.txt
        # py.test --cov=fcs testsuite

5. Type: http://localhost:5000

### Upgrading the application

1. Get the latest version of source code:

        $ cd eea.docker.fcs
        $ git pull origin master

2. Update the application stack, all services should be "Up":

        $ docker-compose up -d
        $ docker-compose ps

### Development instructions

1. Customize docker orchestration for local development:
        
        $ cp docker-compose.override.yml.example docker-compose.override.yml

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
        
        $ docker exec -it fcs.app sh
        # ./manage.py runserver -h 0.0.0.0 -p 5000

### Data import

* Copy the test database in fcs.db container and import into mysql:

        $ docker cp fcs.sql fcs.db:/var/lib/mysql/fcs.sql
        $ docker exec -it fcs.db bash
        # mysql -uroot -p fcs < /var/lib/mysql/fcs.sql

### Syncronise with FGAS/ODS Portal

* Fetch the latest data from a test server:

        $ docker exec fcs.app bash -c "python ./manage.py sync fgases -d 500"
        ./manage.py sync fgases [-d 30]
        ./manage.py sync ods [-d 30]

* In order to sync BDR collections title with the cache server's corresponding undertakings name:

        $ docker exec fcs.app bash -c "./manage.py sync sync_collections_title"

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

### Testing
1. Run tests:

        $ docker exec -it fcs.app sh
        # pip install -r requirements-dev.txt
        # py.test --cov=fcs testsuite

* Generate a coverage report:

        py.test --cov-report html --cov=fcs testsuite
