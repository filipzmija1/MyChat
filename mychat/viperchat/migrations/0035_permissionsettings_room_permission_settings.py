# Generated by Django 4.2.1 on 2023-07-30 19:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0034_alter_room_options'),
    ]

    operations = [
        migrations.CreateModel(
            name='PermissionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('delete_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('delete_user', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_send_invitation', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('members_send_invitation', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='room',
            name='permission_settings',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='viperchat.permissionsettings'),
        ),
    ]
