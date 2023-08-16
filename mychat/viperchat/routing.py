from django.urls import path

from . import consumers

websocket_urlpatterns = [
    path('ws/server/<uuid:server_id>/rooms/<uuid:pk>/', consumers.ChatConsumer.as_asgi()),
]