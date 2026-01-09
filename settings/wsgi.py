import os

from django.core.wsgi import get_wsgi_application

localEnv = True 

if localEnv:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')
else:
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.production')


application = get_wsgi_application()
