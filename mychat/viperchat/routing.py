from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/server/<uuid:server_id>/rooms/<uuid:pk>/', consumers.RoomChatConsumer.as_asgi()),
    path('ws/user/<slug:username>/', consumers.UserChatConsumer.as_asgi()),
]