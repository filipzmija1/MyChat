from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

class User(AbstractUser):
    friends = models.ManyToManyField('self', blank=True, symmetrical=False)
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
    CHOICES = (
        ('friend_request', 'friend_request'),
        ('other', 'other'),
    )
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sender', blank=True, null=True) 
    description = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    receiver = models.ForeignKey(User, on_delete=models.CASCADE, related_name='receiver')
    is_read = models.BooleanField(default=False)
    type = models.CharField(choices=CHOICES, default='other', max_length=64)
