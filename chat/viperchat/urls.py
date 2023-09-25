from django.urls import path

from . import views

urlpatterns = [
    path('server/<uuid:server_id>/rooms/<uuid:pk>/', views.RoomDetail.as_view(), name='room_detail'),
    path('user/<slug:username>', views.UserProfile.as_view(), name='user_detail'),
    path('chat-create/<slug:username>', views.ChatCreate.as_view(), name='chat_create'),
    path('users-chat/<uuid:pk>', views.ChatDetails.as_view(), name='users_chat'),
]