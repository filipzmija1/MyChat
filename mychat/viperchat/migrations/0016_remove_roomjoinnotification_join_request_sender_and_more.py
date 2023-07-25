# Generated by Django 4.2.1 on 2023-07-22 14:16

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0015_rename_privateroomjoinnotification_roomjoinnotification'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='roomjoinnotification',
            name='join_request_sender',
        ),
        migrations.AddField(
            model_name='roomjoinnotification',
            name='invited_user',
            field=models.ForeignKey(default='', on_delete=django.db.models.deletion.CASCADE, related_name='invited_user', to=settings.AUTH_USER_MODEL),
        ),
    ]