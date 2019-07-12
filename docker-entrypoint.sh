#!/bin/bash
set -e

COMMANDS="shell utils db sync runserver api match"

if [ -z "$POSTGRES_ADDR" ]; then
  export POSTGRES_ADDR="postgres"
fi

while ! nc -z $POSTGRES_ADDR 5432; do
  echo "Waiting for Postgres server at '$POSTGRES_ADDR' to accept connections on port 5432..."
  sleep 1s
done

if [ ! -e .skip-db-init ]; then
  touch .skip-db-init
  echo "Running DB CMD: ./manage.py db alembic upgrade head"
  python manage.py db alembic upgrade head
fi

if [ "$DEBUG" = 'True' ]; then
    python manage.py runserver -h 0.0.0.0 -p 5000
fi

if [ -z "$1" ]; then
  echo "Serving on port 5000"
  exec gunicorn manage:app \
                --name european.cache.registry \
                --timeout 120 \
                --bind 0.0.0.0:5000 \
                --access-logfile - \
                --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py "$@"
fi

exec "$@"

