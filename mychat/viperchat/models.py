from django.db import models
from django.contrib.auth.models import AbstractUser, Group

import uuid

class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    username = models.SlugField(unique=True, max_length=150)

    class Meta:
        permissions = [
            ('display_user_profile', 'Can display user informations'),
        ]


class RoomPermissionSettings(models.Model):
    CHOICES = (
        ('Allowed', 'Allowed'),
        ('Forbidden', 'Forbidden'),
    )
    moderators_delete_messages = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_delete_user = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    moderators_send_invitation = models.CharField(max_length=20, choices=CHOICES, default='Allowed')
    members_send_invitation = models.CharField(max_length=20, choices=CHOICES, default='Allowed')


class Room(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=155, unique=True)
    description = models.TextField(blank=True, null=True)
    users = models.ManyToManyField(User, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    is_private = models.BooleanField(default=False)
    permission_settings = models.OneToOneField(RoomPermissionSettings, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        permissions = [
            ("delete_user_from_room", "Can delete user from room"),
            ("display_room_data", "Can see room details"),
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
            ("delete_message_from_room", "Can delete message from room"),
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