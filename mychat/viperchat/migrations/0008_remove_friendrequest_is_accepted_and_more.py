# Generated by Django 4.2.1 on 2023-07-18 18:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0007_alter_friendrequest_is_accepted'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='friendrequest',
            name='is_accepted',
        ),
        migrations.AddField(
            model_name='friendrequest',
            name='status',
            field=models.CharField(choices=[('accepted', 'accepted'), ('canceled', 'canceled'), ('waiting', 'waiting')], default='waiting', max_length=64),
        ),
    ]
