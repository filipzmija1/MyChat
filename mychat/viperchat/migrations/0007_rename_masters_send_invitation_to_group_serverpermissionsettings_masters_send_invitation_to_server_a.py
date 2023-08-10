# Generated by Django 4.2.1 on 2023-08-07 14:46

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0006_alter_serverinvite_options'),
    ]

    operations = [
        migrations.RenameField(
            model_name='serverpermissionsettings',
            old_name='masters_send_invitation_to_group',
            new_name='masters_send_invitation_to_server',
        ),
        migrations.RenameField(
            model_name='serverpermissionsettings',
            old_name='members_send_invitation_to_group',
            new_name='members_send_invitation_to_server',
        ),
        migrations.RenameField(
            model_name='serverpermissionsettings',
            old_name='moderators_send_invitation_to_group',
            new_name='moderators_send_invitation_to_server',
        ),
    ]