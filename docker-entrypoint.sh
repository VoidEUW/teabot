#!/bin/sh
set -e

if [ "$#" -gt 0 ]; then
    exec "$@"
fi

echo "Running database migrations..."
alembic upgrade head

echo "Starting application..."
exec teabot
