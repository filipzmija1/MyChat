from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    username = models.SlugField(unique=True, max_length=150)


class Room(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=155, unique=True)
    description = models.TextField()
    users = models.ManyToManyField(User, blank=True)
    creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='creator')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    

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
    room_creator = models.ForeignKey(User, on_delete=models.CASCADE, related_name='room_creator')
    accepted = models.BooleanField(default=False)