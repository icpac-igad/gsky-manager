#!/bin/sh

CURR_UID=${CURRENT_UID:-9999}

# Notify user about the UID selected
echo "Current UID : $CURR_UID"

# Create user  with selected UID
useradd --shell /bin/bash -u "$CURR_UID" -o -c "" -m app

# Set "HOME" ENV variable for user's home directory
export HOME=/home/app

chown -R app: /home/app

if [ "$DATABASE" = "postgres" ]; then
  echo "Waiting for postgres..."

  while ! nc -z "$POSTGRES_HOST_CMS $POSTGRES_PORT_CMS"; do
    sleep 0.1
  done

  echo "PostgreSQL started"

fi

# Execute process
exec /usr/local/bin/gosu app "$@"
