from channels.db import database_sync_to_async

from .models import Message, Room


@database_sync_to_async
def save_message(author, content, room):
    return Message.objects.create(author=author, content=content, room=room)


@database_sync_to_async
def get_room(room_id):
    return Room.objects.get(id=room_id)