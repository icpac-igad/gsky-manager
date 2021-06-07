#!/bin/sh

if [ "$DATABASE" = "postgres" ]
then
    echo "Waiting for postgres..."

    while ! nc -z $POSTGRES_HOST_CMS $POSTGRES_PORT_CMS; do
      sleep 0.1
    done

    echo "PostgreSQL started"
fi

exec "$@"