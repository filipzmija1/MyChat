# Generated by Django 4.2.1 on 2023-08-05 17:35

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('viperchat', '0018_alter_server_options_alter_user_options_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserPermissionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('only_friends_see_your_profile', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('everyone_see_your_profile', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('hide_email', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_first_name', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_surname', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_friends', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
            ],
        ),
        migrations.AddField(
            model_name='user',
            name='profile_setttings',
            field=models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='viperchat.userpermissionsettings'),
        ),
    ]