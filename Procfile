web: cd taskscheduler && gunicorn taskscheduler.wsgi:application --bind 0.0.0.0:$PORT --workers 3
release: cd taskscheduler && python manage.py migrate && python manage.py collectstatic --noinput
