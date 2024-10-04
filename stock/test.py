import time
from django.test import TestCase, Client
from django.urls import reverse
from .models import Company, ChatRoom, User
from django.utils import timezone
class CheckChatRoomPerformanceTestCase(TestCase):

    def setUp(self):
        self.company = Company.objects.create(
            code=1,
            name='Test Company',
            owner='Owner Name',
            address='Test Address',
            phone='1234567890',
            city='Test City',
            country='Test Country',
            email='test@example.com',
            contract_end_date=timezone.now() + timezone.timedelta(days=365),
            create_user=None
        )
        self.user = User.objects.create(
            username='testuser',
            unique_id='550e8400-e29b-41d4-a716-446655440000',
            company=self.company,
            phone='1234567890',
            email='user@example.com',
            address='User Address'
        )
        for i in range(20000):
            ChatRoom.objects.create(
                name=f'Room {i}',
                owner=self.user,
                status=True,
            )
            print(f"{i} Oda")
        self.client = Client()
        self.client.force_login(self.user)

    def test_check_chat_room_load_time(self):
        url = reverse('destek_odalari', args=[self.company.code])
        start_time = time.time()
        
        response = self.client.get(url)
        
        end_time = time.time()
        load_time = end_time - start_time
        
        print(f'Load time for 1000 chat rooms: {load_time} seconds')

        self.assertEqual(response.status_code, 200, "Sayfa yüklenemedi.")
        self.assertContains(response, 'Room 0')
        self.assertContains(response, 'Room 999')
