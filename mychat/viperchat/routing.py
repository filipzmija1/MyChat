from django.urls import path
from . import consumers

websocket_urlpatterns = [
    path('ws/server/<uuid:server_id>/rooms/<uuid:pk>/', consumers.RoomChatConsumer.as_asgi()),
    path('ws/users-chat/<uuid:pk>/', consumers.UserChatConsumer.as_asgi()),
]