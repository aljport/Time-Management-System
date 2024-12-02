#!/bin/sh

set -e

python manage.py collectstatic --no-input
python manage.py wait_for_db
python manage.py migrate

## Run WSGI socket for NGINX
uwsgi --socket :${PORT} --workers 4 --master --enable-threads --module app.wsgi