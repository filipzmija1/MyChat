# Generated by Django 4.2.1 on 2023-08-02 21:41

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0006_serverpermissionsettings_masters_create_room_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='server',
            options={'permissions': [('create_room_in_server', 'Can create room in server')]},
        ),
    ]