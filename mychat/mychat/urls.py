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
    path('server/<uuid:server_id>/rooms/<uuid:pk>/', vchat.RoomDetail.as_view(), name='room_detail'),
    path('server/<uuid:pk>/create-room/', vchat.CreateRoom.as_view(), name='create_room'),
    path('accounts/', include('allauth.urls')),
    path('rooms/', vchat.ServerList.as_view(), name='servers'),
    path('user/<slug:username>', vchat.UserProfile.as_view(), name='user_detail'),
    path('server/<uuid:server_id>/rooms/<uuid:pk>/edit', vchat.RoomEdit.as_view(), name='room_edit'),
    path('edit-user/<slug:username>', vchat.UserProfileEdit.as_view(), name='edit_profile'),
    path('edit-user/<slug:username>/permissions', vchat.UserProfilePermissions.as_view(), name='change_profile_permissions'),
    path('change-passsword/<slug:username>', vchat.ChangePassword.as_view(), name='change_password'),
    path('search/', vchat.SearchUserOrRoom.as_view(), name='search'),
    path('delete-friend/<slug:username>', vchat.DeleteFriend.as_view(), name='delete_friend'),
    path('friend-request/<slug:username>', vchat.FriendNotifiaction.as_view(), name='friend_notification'),
    path('user/<slug:username>/notifications/delete/confirm', vchat.NotifiacationsDeleteConfirm.as_view(), name='notification_delete_confirm'),
    path('user/<slug:username>/notifications/delete/<uuid:pk>', vchat.NotificationDelete.as_view(), name='notification_delete'),
    path('user/<slug:username>/notifications/delete', vchat.AllNotificationsDelete.as_view(), name='all_notifications_delete'),
    path('user/<slug:username>/notifications/navigator', vchat.Notifications.as_view(), name='notifications'),
    path('user/<slug:username>/notifications/set-unread/<uuid:pk>', vchat.NotificationSetUnread.as_view(), name='set_unread'),
    path('user/<slug:username>/notifications', vchat.NotificationList.as_view(), name='notification_list'),
    path('user/<slug:username>/notifications-unread', vchat.NotificationUnreadList.as_view(), name='notification_unread_list'),
    path('user/<slug:username>/notifications-read', vchat.NotificationsReadList.as_view(), name='notification_read_list'),
    path('user/<slug:username>/notification-detail/<uuid:pk>', vchat.NotificationDetail.as_view(), name='notification_detail'),
    path('user/<slug:username>/notification/change/<uuid:pk>', vchat.NotificationUpdate.as_view(), name='notification_update'),
    path('user/<slug:username>/friend-requests', vchat.FriendRequestList.as_view(), name='friend_request_list'),
    path('friend-requests/<uuid:pk>', vchat.FriendRequestAnswer.as_view(), name='friend_request_detail'),
    path('request-delete/<uuid:pk>', vchat.FriendRequestDelete.as_view(), name='friend_request_delete'),
    path('delete-message/<uuid:pk>', vchat.DeleteMessage.as_view(), name='delete_message'),
    path('join-server/<uuid:pk>', vchat.JoinServer.as_view(), name='join_server'),
    path('delete-user/server/<uuid:server_id>/user/<slug:username>', vchat.DeleteUserFromServer.as_view(), name='delete_user_from_server'),
    path('server/<uuid:server_id>/users', vchat.ServerUsersManage.as_view(), name='server_users_list'),
    path('messages/<uuid:pk>', vchat.MessageEdit.as_view(), name='message_edit'),
    path('create-server/', vchat.CreateServer.as_view(), name='create_server'),
    path('server-details/<uuid:pk>', vchat.ServerDetails.as_view(), name='server_detail'),
    path('server-initial/<uuid:pk>', vchat.GiveInitialPermissions.as_view(), name='server_initial'),
    path('server-edit/<uuid:pk>', vchat.ServerEdit.as_view(), name='server_edit'),
    path('server-groups/management/<uuid:pk>', vchat.ServerGroupsManagement.as_view(), name='server_groups_management'),
    path('server-groups/management/change/<uuid:pk>', vchat.ServerPermissionChange.as_view(), name='permissions_change'),
    path('user/<slug:username>/servers', vchat.UserServerList.as_view(), name='logged_user_servers'),
    path('user/<slug:username>/server/<uuid:server_id>/group/<slug:name>', vchat.UserGroupEdit.as_view(), name='user_group_edit'),
    path('server/<uuid:pk>/invite/', vchat.SearchUserToInvite.as_view(), name='server_invite'),
    path('server/<uuid:pk>/confirm-leave', vchat.ServerLeaveConfirm.as_view(), name='server_leave_confirm'),
    path('server/<uuid:pk>/leave', vchat.ServerLeave.as_view(), name='server_leave'),
    path('server/<uuid:pk>/invite/<slug:username>', vchat.ServerInviteSend.as_view(), name='send_server_invite'),
    path('server/<uuid:pk>/invite/<slug:username>/delete/<uuid:invite_id>', vchat.ServerInviteDelete.as_view(), name='delete_server_invite'),
    path('user/<slug:username>/server-invites', vchat.UserServerInvitesList.as_view(), name='user_server_invites'),
    path('user/<slug:username>/server-invites/<uuid:pk>', vchat.ServerInviteDetail.as_view(), name='server_invite_detail'),
    path('user/<slug:username>/server-invites/<uuid:pk>/delete', vchat.ServerInviteDelete.as_view(), name='server_invite_delete'),

]
