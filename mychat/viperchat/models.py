from django.db import models
from django.contrib.auth.models import AbstractUser

import uuid

class CustomUser(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    username = models.SlugField(unique=True, max_length=150)


class Room(models.Model):
    id = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        primary_key=True,
        editable=False
    )
    name = models.CharField(max_length=155)
    description = models.TextField()
    users = models.ManyToManyField(CustomUser, blank=True)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator')
    is_private = models.BooleanField(default=False)

    def __str__(self):
        return self.name


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    