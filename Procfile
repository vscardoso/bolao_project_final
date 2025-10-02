# Heroku/Railway Procfile
web: gunicorn bolao_config.wsgi:application --env DJANGO_SETTINGS_MODULE=bolao_config.settings_production
release: python manage.py migrate --settings=bolao_config.settings_production --noinput
