# Generated by Django 4.2.1 on 2023-07-22 10:05

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0011_remove_privacyroomnotification_description'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='PrivacyRoomNotification',
            new_name='PrivateRoomJoinNotification',
        ),
    ]
