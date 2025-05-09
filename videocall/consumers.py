# videocall/consumers.py
import json
from channels.generic.websocket import AsyncWebsocketConsumer

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['roomID']
        self.room_group_name = f'videocall_{self.room_id}'

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )
        print(f'Disconnected from room {self.room_id}')

    async def receive(self, text_data):
        receive_dict = json.loads(text_data)
        message = receive_dict['message']
        action = receive_dict['action']
        peer = receive_dict.get('peer', '')

        # Добавляем URL аватарки в сообщение new-peer
        if action == 'new-peer':
            user = self.scope['user']
            avatar_url = user.avatar.url if user.is_authenticated and user.avatar else '/static/main/img/noimageavatar.svg'
            message['avatar_url'] = avatar_url

        receive_dict['message']['receiver_channel_name'] = self.channel_name

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'send_sdp',
                'receive_dict': receive_dict
            }
        )

    async def send_sdp(self, event):
        receive_dict = event['receive_dict']
        await self.send(text_data=json.dumps(receive_dict))