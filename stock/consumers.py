import json
from channels.generic.websocket import AsyncWebsocketConsumer
from channels.db import database_sync_to_async
import datetime

class ChatConsumer(AsyncWebsocketConsumer):
    async def connect(self):
        self.room_name = self.scope['url_route']['kwargs']['room_name']
        self.room_group_name = f'chat_{self.room_name}'
        self.username = self.scope['user'].username  # Kullanıcı adı
        self.user_id = self.scope['user'].id  # Kullanıcı ID
        self.user_tag = self.scope['user'].tag  # Kullanıcı etiketi

        # Odaya katıl
        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )
        await self.accept()

        # Odanın diğer üyelerine katılım mesajı gönder
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_image = await self.get_user_profile_image(self.user_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_joined',
                'username': self.username,
                'profile_image': profile_image,
                'message': f'{self.username}{(" (" + self.user_tag + ")" if self.user_tag else "")} desteğe katıldı.',
                'timestamp': timestamp
            }
        )

    async def disconnect(self, close_code):
        # Odayı terk et
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

        # Odanın diğer üyelerine ayrılma mesajı gönder
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        profile_image = await self.get_user_profile_image(self.user_id)
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'user_left',
                'username': self.username,
                'profile_image': profile_image,
                'message': f'{self.username} destekten ayrıldı.',
                'timestamp': timestamp
            }
        )

    async def receive(self, text_data):
        text_data_json = json.loads(text_data)
        message = text_data_json['message']
        username = text_data_json.get('username')
        user_id = text_data_json.get('user_id')

        # Kullanıcıyı ID üzerinden al
        user = await self.get_user(user_id)

        # Profil resmini al (varsa)
        profile_image = user.profile_image.url if user and user.profile_image else ''

        # Oda ve mesajı veritabanına kaydet
        chat_room = await self.save_or_get_chat_room(self.room_name)
        await self.save_message(chat_room, user, message)

        # Mesaj gönderim zamanını al
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        # Mesajı odadaki tüm kullanıcılara gönder
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                'type': 'chat_message',
                'username': username,
                'message': message,
                'user_id': user_id,
                'profile_image': profile_image,
                'timestamp': timestamp
            }
        )

    async def chat_message(self, event):
        message = event['message']
        username = event['username']
        user_id = event['user_id']
        profile_image = event['profile_image']
        timestamp = event['timestamp']

        # Mesajı WebSocket üzerinden gönder
        await self.send(text_data=json.dumps({
            'type': 'chat_message',
            'message': message,
            'username': username,
            'user_id': user_id,
            'profile_image': profile_image,
            'timestamp': timestamp
        }))

    async def user_joined(self, event):
        username = event['username']
        profile_image = event['profile_image']
        message = event['message']
        timestamp = event['timestamp']

        # Kullanıcı katıldığında WebSocket üzerinden mesaj gönder
        await self.send(text_data=json.dumps({
            'type': 'user_joined',
            'username': username,
            'profile_image': profile_image,
            'message': message,
            'timestamp': timestamp
        }))

    async def user_left(self, event):
        username = event['username']
        profile_image = event['profile_image']
        message = event['message']
        timestamp = event['timestamp']

        # Kullanıcı ayrıldığında WebSocket üzerinden mesaj gönder
        await self.send(text_data=json.dumps({
            'type': 'user_left',
            'username': username,
            'profile_image': profile_image,
            'message': message,
            'timestamp': timestamp
        }))

    @database_sync_to_async
    def save_or_get_chat_room(self, room_name):
        from stock.models import ChatRoom
        chat_room, created = ChatRoom.objects.get_or_create(name=room_name)
        return chat_room

    @database_sync_to_async
    def save_message(self, chat_room, user, message):
        from stock.models import Message
        return Message.objects.create(
            room=chat_room,
            user=user,
            content=message
        )
    
    @database_sync_to_async
    def get_user(self, user_id):
        from .models import User
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return None

    @database_sync_to_async
    def get_user_profile_image(self, user_id):
        from .models import User
        try:
            user = User.objects.get(id=user_id)
            return user.profile_image.url if user.profile_image else ''
        except User.DoesNotExist:
            return ''
