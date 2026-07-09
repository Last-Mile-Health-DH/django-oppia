#!/bin/sh

echo 'Running migrations...'
python manage.py migrate

echo 'Compile the SCSS files...'
python manage.py compilescss

echo 'Collecting static files...'
python manage.py collectstatic --no-input

echo 'Loading initial data...'
python manage.py loaddata oppia/fixtures/default_badges.json
python manage.py loaddata oppia/fixtures/default_gamification_events.json

echo 'Ensuring admin user exists...'
python manage.py shell -c "
import os
from django.contrib.auth import get_user_model

username = os.environ.get('DJANGO_SUPERUSER_USERNAME')
User = get_user_model()

if username and not User.objects.filter(username=username).exists():
    User.objects.create_superuser(
        username,
        os.environ.get('DJANGO_SUPERUSER_EMAIL', ''),
        os.environ.get('DJANGO_SUPERUSER_PASSWORD'),
    )
"

echo 'Starting Django Server...'
exec gunicorn oppiamobile.wsgi:application --bind 0.0.0.0:8000