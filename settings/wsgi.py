import os
from django.core.wsgi import get_wsgi_application

# --- CAMBIO: Forzamos SIEMPRE settings.settings ---
# Ya no hay if/else. En Dokploy usaremos este archivo.
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

application = get_wsgi_application()