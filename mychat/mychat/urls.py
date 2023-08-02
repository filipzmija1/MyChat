"""
URL configuration for mychat project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path, include
import viperchat.views as vchat

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', vchat.HomePage.as_view(), name='home'),
    path('server/<uuid:pk>/create-room/', vchat.CreateRoom.as_view(), name='create_room'),
    path('accounts/', include('allauth.urls')),
    path('rooms/', vchat.RoomList.as_view(), name='rooms'),
    path('rooms/<uuid:pk>', vchat.RoomDetail.as_view(), name='room_detail'),
    path('user/<slug:username>', vchat.UserProfile.as_view(), name='user_detail'),
    path('edit-user/<slug:username>', vchat.UserProfileEdit.as_view(), name='edit_profile'),
    path('change-passsword/<slug:username>', vchat.ChangePassword.as_view(), name='change_password'),
    path('search/', vchat.SearchUserOrRoom.as_view(), name='search'),
    path('delete-friend/<slug:username>', vchat.DeleteFriend.as_view(), name='delete_friend'),
    path('friend-request/<slug:username>', vchat.FriendNotifiaction.as_view(), name='friend_notification'),
    path('user/<slug:username>/notifications', vchat.NotificationList.as_view(), name='notification_list'),
    path('user/<slug:username>/friend-requests', vchat.FriendRequestList.as_view(), name='friend_request_list'),
    path('friend-requests/<uuid:pk>', vchat.FriendRequestAnswer.as_view(), name='friend_request_detail'),
    path('request-delete/<uuid:pk>', vchat.FriendRequestDelete.as_view(), name='friend_request_delete'),
    path('user/<slug:username>/your-rooms', vchat.UserOwnRooms.as_view(), name='logged_user_rooms'),
    path('delete-message/<uuid:pk>', vchat.DeleteMessage.as_view(), name='delete_message'),
    path('join-room/<uuid:pk>', vchat.JoinRoom.as_view(), name='join_room'),
    path('room-management/<uuid:pk>', vchat.RoomManagement.as_view(), name='room_management'),
    path('room-management/<uuid:pk>/groups', vchat.RoomRanksDisplay.as_view(), name='room_groups_management'),
    path('room-management/<uuid:pk>/groups/<slug:name>', vchat.UserRankDetail.as_view(), name='user_rank_edit'),
    path('delete-user/room/<uuid:pk>/user/<slug:username>', vchat.DeleteUserFromRoom.as_view(), name='delete_user_from_room'),
    path('rank-change/room/<uuid:pk>/user/<slug:username>/group/<slug:name>', vchat.UserRankEdit.as_view(), name='user_rank_change'),
    path('room/<uuid:pk>/users', vchat.RoomUsersList.as_view(), name='room_users_list'),
    path('messages/<uuid:pk>', vchat.MessageEdit.as_view(), name='message_edit'),
    path('create-server/', vchat.CreateServer.as_view(), name='create_server'),
    path('server_details/<uuid:pk>', vchat.ServerDetails.as_view(), name='server_detail'),
    path('server-initial/<uuid:pk>', vchat.GiveInitialPermissions.as_view(), name='server_initial'),

]
