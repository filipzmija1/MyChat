from django.urls import path

from . import views

urlpatterns = [
    path('server/<uuid:server_id>/rooms/<uuid:pk>/', views.RoomDetail.as_view(), name='room_detail'),
    path('user/<slug:username>', views.UserProfile.as_view(), name='user_detail'),
]