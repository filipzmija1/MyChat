# Generated by Django 4.2.1 on 2023-06-04 05:50

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0002_customuser_is_good'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='customuser',
            name='is_good',
        ),
    ]
