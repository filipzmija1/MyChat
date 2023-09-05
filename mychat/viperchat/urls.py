from django.urls import path

from . import views

urlpatterns = [
    path('server/<uuid:server_id>/rooms/<uuid:pk>/', views.RoomDetail.as_view(), name='room_detail'),
]