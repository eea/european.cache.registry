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

#create database for service
if ! mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "use $DB_NAME;"; then
  echo "CREATE DATABASE $DB_NAME"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE DATABASE $DB_NAME CHARACTER SET utf8 COLLATE utf8_general_ci;"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "CREATE USER '$DB_USER'@'%' IDENTIFIED BY '$DB_PASS';"
  mysql -h mysql -u root -p$MYSQL_ROOT_PASSWORD -e "GRANT ALL PRIVILEGES ON $DB_NAME.* TO '$DB_USER'@'%';"
fi

if [ ! -e .skip-db-init ]; then
  touch .skip-db-init
  echo "Running DB CMD: ./manage.py db init"
  python manage.py db init
fi

if [ -z "$1" ]; then
  echo "Serving on port 5000"
  exec gunicorn manage:app \
                --name fgas \
                --bind 0.0.0.0:5000 \
                --access-logfile - \
                --error-logfile -
fi

if [[ $COMMANDS == *"$1"* ]]; then
  exec python manage.py "$@"
fi

exec "$@"
