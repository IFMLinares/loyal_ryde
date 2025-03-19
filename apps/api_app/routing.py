from django.urls import path
from . import consumers

websocket_urlpatterns = [
	path('notifications/', consumers.NotificationConsummer.as_asgi()),
    path('ws/site_notifications/', consumers.SiteNotificationConsumer.as_asgi()),  # Nueva ruta para el sitio web
]