from django.db import models
from django.contrib.auth.models import AbstractUser

class CustomUser(AbstractUser):
    friends = models.ManyToManyField('self', blank=True)
    username = models.SlugField(unique=True, max_length=150)


class Room(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField()
    users = models.ManyToManyField(CustomUser)
    creator = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name='creator')
    is_private = models.BooleanField(default=False)


class Message(models.Model):
    room = models.ForeignKey(Room, on_delete=models.CASCADE)
    author = models.ForeignKey(CustomUser, on_delete=models.CASCADE)
    content = models.TextField()
    date_created = models.DateTimeField(auto_now_add=True)
    date_edited = models.DateTimeField(null=True)
    