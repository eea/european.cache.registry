#!/bin/bash
set -e

COMMANDS="shell utils db sync runserver api match"

if [ -z "$POSTGRES_ADDR" ]; then
    POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for PostgreSQL server at '$POSTGRES_ADDR' to accept connections..."
  sleep 3s
done

if [ ! -e .skip-db-init ]; then
  touch .skip-db-init
  echo "Running DB CMD: ./manage.py db init"
  python manage.py db init
fi

if [ -z "$1" ]; then
  echo "Serving on port 5000"
  exec waitress-serve --port 5000 manage:app
fi

if [[ "$1" == "--"* ]]; then
  exec waitress-serve "$@" manage:app
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py "$@"
fi

exec "$@"
