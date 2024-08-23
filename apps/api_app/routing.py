from django.urls import path

from . import consumers

websocket_urlpatterns = [
	path('notifications/', consumers.NotificationConsummer.as_asgi()),
]