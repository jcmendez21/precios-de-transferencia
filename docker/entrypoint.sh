#!/bin/bash
set -e

echo "Applying migrations..."
python manage.py migrate --noinput

exec "$@"
