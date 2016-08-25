#!/bin/bash
set -e

COMMANDS="shell utils db sync runserver api match"

if [ -z "$MYSQL_ADDR" ]; then
    MYSQL_ADDR="mysql"
fi

while ! nc -z $MYSQL_ADDR 3306; do
  echo "Waiting for MySQL server at '$MYSQL_ADDR' to accept connections on port 3306..."
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
