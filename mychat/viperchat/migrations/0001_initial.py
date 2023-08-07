# Generated by Django 4.2.1 on 2023-08-07 10:19

from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion
import django.utils.timezone
import uuid


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        ('auth', '0012_alter_user_first_name_max_length'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('password', models.CharField(max_length=128, verbose_name='password')),
                ('last_login', models.DateTimeField(blank=True, null=True, verbose_name='last login')),
                ('is_superuser', models.BooleanField(default=False, help_text='Designates that this user has all permissions without explicitly assigning them.', verbose_name='superuser status')),
                ('first_name', models.CharField(blank=True, max_length=150, verbose_name='first name')),
                ('last_name', models.CharField(blank=True, max_length=150, verbose_name='last name')),
                ('email', models.EmailField(blank=True, max_length=254, verbose_name='email address')),
                ('is_staff', models.BooleanField(default=False, help_text='Designates whether the user can log into this admin site.', verbose_name='staff status')),
                ('is_active', models.BooleanField(default=True, help_text='Designates whether this user should be treated as active. Unselect this instead of deleting accounts.', verbose_name='active')),
                ('date_joined', models.DateTimeField(default=django.utils.timezone.now, verbose_name='date joined')),
                ('username', models.SlugField(max_length=150, unique=True)),
                ('friends', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
                ('groups', models.ManyToManyField(blank=True, help_text='The groups this user belongs to. A user will get all permissions granted to each of their groups.', related_name='user_set', related_query_name='user', to='auth.group', verbose_name='groups')),
                ('user_permissions', models.ManyToManyField(blank=True, help_text='Specific permissions for this user.', related_name='user_set', related_query_name='user', to='auth.permission', verbose_name='user permissions')),
            ],
            options={
                'permissions': [('friends_see_profile', 'Friends can see user profile'), ('change_user_group', 'Can change users group'), ('everyone_see_profile', 'Everyone can see user profile')],
            },
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Room',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=155)),
                ('description', models.TextField()),
                ('is_private', models.BooleanField(default=False)),
            ],
            options={
                'permissions': [('delete_user_from_server', 'Can delete user from server'), ('display_private_room_data', 'Can see private room details')],
            },
        ),
        migrations.CreateModel(
            name='ServerPermissionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('masters_create_room', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('masters_send_invitation_to_group', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('masters_delete_user', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('masters_delete_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('masters_send_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('masters_can_see_private_rooms', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('masters_can_edit_users_group', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('masters_can_edit_rooms', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_create_room', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('moderators_delete_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_delete_user', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_send_invitation_to_group', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_send_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('moderators_can_see_private_rooms', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('moderators_can_edit_rooms', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('members_create_room', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('members_delete_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('members_send_invitation_to_group', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('members_send_messages', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('members_can_see_private_rooms', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
            ],
        ),
        migrations.CreateModel(
            name='UserPermissionSettings',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('everyone_see_your_profile', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Allowed', max_length=20)),
                ('hide_email', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_first_name', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_surname', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('hide_friends', models.CharField(choices=[('Allowed', 'Allowed'), ('Forbidden', 'Forbidden')], default='Forbidden', max_length=20)),
                ('user', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Server',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('name', models.CharField(max_length=155, unique=True)),
                ('description', models.TextField(blank=True, null=True)),
                ('is_private', models.BooleanField(default=True)),
                ('creator', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='server_creator', to=settings.AUTH_USER_MODEL)),
                ('permission_settings', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='viperchat.serverpermissionsettings')),
                ('users', models.ManyToManyField(blank=True, to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'permissions': [('create_room_in_server', 'Can create room in server'), ('send_messages_in_server', 'Can send messages in server'), ('delete_masters_from_server', 'Can delete users in master group'), ('delete_moderators_from_server', 'Can delete users in moderators group'), ('delete_members_from_server', 'Can delete users in members group'), ('edit_permissions_in_server', 'Can modify groups permissions'), ('edit_moderators_group', 'Can change moderators group'), ('edit_members_group', 'Can change members group'), ('edit_masters_group', 'Can change masters group'), ('edit_rooms_in_server', 'Can change rooms data in server')],
            },
        ),
        migrations.CreateModel(
            name='RoomInvite',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('accepted', models.BooleanField(default=False)),
                ('invitation_sender', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invitation_sender', to=settings.AUTH_USER_MODEL)),
                ('invited_user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='invited_user', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viperchat.room')),
            ],
            options={
                'permissions': [('send_invitation', 'Can send invitations to private room')],
            },
        ),
        migrations.AddField(
            model_name='room',
            name='server',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='viperchat.server'),
        ),
        migrations.CreateModel(
            name='Notification',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('is_read', models.BooleanField(default=False)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('content', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('date_edited', models.DateTimeField(blank=True, null=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='author', to=settings.AUTH_USER_MODEL)),
                ('message_receiver', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='message_receiver', to=settings.AUTH_USER_MODEL)),
                ('room', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='viperchat.room')),
            ],
            options={
                'permissions': [('delete_message_from_server', 'Can delete message from server')],
            },
        ),
        migrations.CreateModel(
            name='FriendRequest',
            fields=[
                ('id', models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True, serialize=False, unique=True)),
                ('description', models.TextField()),
                ('date_created', models.DateTimeField(auto_now_add=True)),
                ('status', models.CharField(choices=[('accepted', 'accepted'), ('canceled', 'canceled'), ('waiting', 'waiting')], default='waiting', max_length=64)),
                ('receiver', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='receiver', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
