# Generated by Django 4.2.1 on 2023-08-07 14:44

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0005_alter_serverinvite_receiver_and_more'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='serverinvite',
            options={'permissions': [('send_invitation', 'Can send invitations to private servers')]},
        ),
    ]