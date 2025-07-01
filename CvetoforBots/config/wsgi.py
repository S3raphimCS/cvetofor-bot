import os
import sys

from django.core.wsgi import get_wsgi_application


if os.getenv('ENVIRONMENT') == 'production':
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'CvetoforBots.config.settings.production',
    )
    print(f'--> Running manage.py with production environment: {sys.argv}')
else:
    os.environ.setdefault(
        'DJANGO_SETTINGS_MODULE',
        'CvetoforBots.config.settings.development',
    )
    print(f'--> Running manage.py with development environment: {sys.argv}')


application = get_wsgi_application()
