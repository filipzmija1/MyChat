# Generated by Django 4.2.1 on 2023-07-18 18:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0006_remove_notification_sender_remove_notification_type_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='friendrequest',
            name='is_accepted',
            field=models.BooleanField(default=False),
        ),
    ]
