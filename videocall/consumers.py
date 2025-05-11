import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_id = self.scope['url_route']['kwargs']['roomID']
        self.room_group_name = f'videocall_{self.room_id}'
        self.user = self.scope['user']

        # Проверяем, является ли пользователь участником занятия
        if not await self.is_user_participant():
            await self.send(text_data=json.dumps({
                'action': 'connection_rejected',
                'message': {'reason': 'Вы не являетесь участником этого занятия.'}
            }))
            await self.close()
            return


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

    @database_sync_to_async
    def is_user_participant(self):

        from django.contrib.auth import get_user_model
        from chat.models import Lesson

        CustomUser = get_user_model()
        try:

            lesson = Lesson.objects.get(call_link__contains=self.room_id)

            return self.user == lesson.student or self.user == lesson.teacher
        except Lesson.DoesNotExist:
            return False