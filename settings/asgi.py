"""
ASGI config for settings project.
"""

import os
from django.core.asgi import get_asgi_application

# 1. Configurar la variable de entorno PRIMERO
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'settings.settings')

# 2. Inicializar Django AHORA (Esto carga apps y modelos)
django_asgi_app = get_asgi_application()

# -----------------------------------------------------------
# 3. IMPORTAR EL RESTO DESPUÉS DE INICIALIZAR DJANGO
# (Si importas esto antes, da error porque Django no está listo)
# -----------------------------------------------------------
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from django_channels_jwt_auth_middleware.auth import JWTAuthMiddlewareStack
from apps.api_app.routing import websocket_urlpatterns

application = ProtocolTypeRouter({
    'http': django_asgi_app,
    'websocket': AllowedHostsOriginValidator(
        JWTAuthMiddlewareStack(
            URLRouter(websocket_urlpatterns)
        )
    )
})