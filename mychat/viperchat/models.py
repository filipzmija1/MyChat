from django.db import models
from django.contrib.auth.models import AbstractUser, Group

import uuid

class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    username = models.SlugField(unique=True, max_length=150)

    class Meta:
        permissions = [
            ('friends_see_profile', 'Friends can see user profile'),
            ('change_user_group', 'Can change users group'),    #   Modify users group in server
            ('everyone_see_profile', 'Everyone can see user profile')
        ]


class UserPermissionSettings(models.Model):
    CHOICES = (
        ('Allowed', 'Allowed'),
        ('Forbidden', 'Forbidden'),
    )
    everyone_see_your_profile = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    hide_email = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    hide_first_name = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    hide_surname = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    hide_friends = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    user = models.OneToOneField(User, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.user.username


class ServerPermissionSettings(models.Model):
    CHOICES = (
        ('Allowed', 'Allowed'),
        ('Forbidden', 'Forbidden'),
    )
    #   Masters permissions
    masters_create_room = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    masters_send_invitation_to_group = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    masters_delete_user = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    masters_delete_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    masters_send_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    masters_can_see_private_rooms = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    masters_can_edit_users_group = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    masters_can_edit_rooms = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    #   Moderators permissions
    moderators_create_room = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    moderators_delete_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_delete_user = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_send_invitation_to_group = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_send_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_can_see_private_rooms = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    moderators_can_edit_rooms = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    #   Members permissions
    members_create_room = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    members_delete_messages = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')
    members_send_invitation_to_group = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    members_send_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    members_can_see_private_rooms = models.CharField(max_length=20, choices=CHOICES, default='Forbidden')


class Server(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=155, unique=True)
    description = models.TextField(null=True, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='server_creator')
    users = models.ManyToManyField(User, blank=True)
    permission_settings = models.OneToOneField(ServerPermissionSettings, on_delete=models.CASCADE, null=True, blank=True)
    is_private = models.BooleanField(default=True)

    class Meta:
        permissions = [
            ('create_room_in_server', 'Can create room in server'),
            ('send_messages_in_server', 'Can send messages in server'),
        
            ('delete_masters_from_server', 'Can delete users in master group'),
            ('delete_moderators_from_server', 'Can delete users in moderators group'),
            ('delete_members_from_server', 'Can delete users in members group'),

            ('edit_permissions_in_server', 'Can modify groups permissions'),

            ('edit_moderators_group', 'Can change moderators group'),
            ('edit_members_group', 'Can change members group'),
            ('edit_masters_group', 'Can change masters group'),
            ('edit_rooms_in_server', 'Can change rooms data in server'),
        ]

    def __str__(self):
        return self.name


class Room(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=155)
    description = models.TextField()
    is_private = models.BooleanField(default=False)
    server = models.ForeignKey(Server, on_delete=models.CASCADE)

    class Meta:
        permissions = [
            ("delete_user_from_server", "Can delete user from server"),
            ("display_private_room_data", "Can see private room details"),
        ]

    def __str__(self):
        return self.name


class Message(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    room = models.ForeignKey(Room, on_delete=models.CASCADE, blank=True, null=True)
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='author')
    message_receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='message_receiver', blank=True, null=True)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True, blank=True)

    class Meta:
        permissions = [
            ("delete_message_from_server", "Can delete message from server"),
        ]

    def __str__(self):
        return self.content

class Notification(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE)
    is_read = models.BooleanField(default=False)


class FriendRequest(models.Model):
    CHOICES = (
        ('accepted', 'accepted'),
        ('canceled', 'canceled'),
        ('waiting', 'waiting'),
    )
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', blank=True, null=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    status = models.CharField(choices=CHOICES, max_length=64, default='waiting')


class RoomInvite(models.Model):
    id = models.UUIDField(
    default=uuid.uuid4,
    unique=True,
    primary_key=True,
    editable=False
)
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    invited_user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_user')
    invitation_sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invitation_sender')
    accepted = models.BooleanField(default=False)
    class Meta:
        permissions = [
            ("send_invitation", "Can send invitations to private room"),
        ]