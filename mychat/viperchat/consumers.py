import json

from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

from .models import Message, Room, Server


class RoomChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.server_id = self.scope["url_route"]["kwargs"]["server_id"]
        self.room_id = self.scope["url_route"]["kwargs"]["pk"]
        self.room_group_name = f"chat_{self.room_id}"

        # Join room group
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Leave room group
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Receive message from WebSocket
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json["message"]
        username = self.scope["user"].username
        room = await get_room(self.room_id)
        # Send message to room group
        await self.channel_layer.group_send(
            self.room_group_name, {"type": "chat.message", "message": message, "username": username}
        )
        # Save messages to database
        await save_room_message(self.scope['user'], message, room)

    # Receive message from room group
    async def chat_message(self, event):
        message = event["message"]
        username = event['username']
        # Send message to WebSocket
        await self.send(text_data=json.dumps({"message":f'{username}: {message}'}))


@database_sync_to_async
def save_room_message(author, content, room):
    return Message.objects.create(author=author, content=content, room=room)


@database_sync_to_async
def get_room(room_id):
    return Room.objects.get(id=room_id)


@database_sync_to_async
def save_private_message(author, content, receiver):
    return Message.objects.create(author=author, content=content, message_receiver=receiver)


@database_sync_to_async
def get_server(server_id):
    return Server.objects.get(id=server_id)