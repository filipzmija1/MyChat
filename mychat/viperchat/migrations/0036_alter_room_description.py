# Generated by Django 4.2.1 on 2023-07-30 21:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0035_permissionsettings_room_permission_settings'),
    ]

    operations = [
        migrations.AlterField(
            model_name='room',
            name='description',
            field=models.TextField(blank=True, null=True),
        ),
    ]
