# main/consumers.py

import json
from channels.generic.websocket import AsyncWebsocketConsumer
from django.utils import timezone
from .models import Message


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.user = self.scope["user"]
        self.room_name = f"chat_{self.user.id}_{self.receiver_id}"
        self.room_group_name = f"chat_{self.user.id}_{self.receiver_id}"

        # Присоединяемся к группе чата
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Отключаемся от группы чата
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    # Получение сообщения от клиента
    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message_content = text_data_json['message']
        timestamp = timezone.now().strftime('%j %B %H:%M')

        # Сохраняем сообщение в базу данных
        message = Message.objects.create(
            sender=self.user,
            receiver_id=self.receiver_id,
            content=message_content,
            timestamp=timezone.now(),
        )

        # Отправляем сообщение всем клиентам в группе
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'sender': self.user.username,
                'content': message_content,
                'timestamp': timestamp,
                'image': message.image.url if message.image else None,
                'video': message.video.url if message.video else None,
            },
        )

    # Обработка сообщения, отправленного в группу
    async def chat_message(self, event):
        sender = event['sender']
        content = event['content']
        timestamp = event['timestamp']
        image = event['image']
        video = event['video']

        # Отправка сообщения на WebSocket клиенту
        await self.send(
            text_data=json.dumps(
                {
                    'sender': sender,
                    'content': content,
                    'timestamp': timestamp,
                    'image': image,
                    'video': video,
                }
            )
        )
