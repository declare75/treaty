import json
from channels.generic.websocket import AsyncWebsocketConsumer


class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.receiver_id = self.scope['url_route']['kwargs']['receiver_id']
        self.room_group_name = f'chat_{self.receiver_id}'

        # Подключение к группе
        await self.channel_layer.group_add(self.room_group_name, self.channel_name)

        await self.accept()

    async def disconnect(self, close_code):
        # Отключение от группы
        await self.channel_layer.group_discard(self.room_group_name, self.channel_name)

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        content = text_data_json['content']
        sender = text_data_json['sender']

        # Отправка сообщения в группу
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'content': content,
                'sender': sender,
            }
        )

    async def chat_message(self, event):
        content = event['content']
        sender = event['sender']

        # Отправка сообщения в WebSocket
        await self.send(text_data=json.dumps({
            'content': content,
            'sender': sender,
        }))
