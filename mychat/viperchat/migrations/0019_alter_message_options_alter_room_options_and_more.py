# Generated by Django 4.2.1 on 2023-07-27 11:46

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0018_rename_roomjoinnotification_roominvite'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='message',
            options={'permissions': [('delete_chat_message', 'Can delete message')]},
        ),
        migrations.AlterModelOptions(
            name='room',
            options={'permissions': [('delete_user_from_room', 'Can delete user from room')]},
        ),
        migrations.AlterField(
            model_name='message',
            name='date_edited',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]