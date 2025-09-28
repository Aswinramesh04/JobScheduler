web: cd taskscheduler && gunicorn taskscheduler.wsgi:application --bind 0.0.0.0:$PORT
release: cd taskscheduler && python manage.py migrate
