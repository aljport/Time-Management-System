from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Calendar_Event, Notifications


class CreateEventViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_create_event(self):
        url = reverse('create_event')
        data = {
            'title': 'Team Meeting',
            'description': 'Discuss project updates',
            'start_time': '2024-10-28T14:00:00Z',
            'end_time': '2024-10-28T15:00:00Z',
            'attendee': [self.user.id]
        }
        
        response = self.client.post(url, data)
        
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Calendar_Event.objects.filter(title='Team Meeting').exists())
        event = Calendar_Event.objects.get(title='Team Meeting')
        self.assertEqual(event.description, 'Discuss project updates')
        self.assertIn(self.user, event.attendee.all())
        self.assertTrue(Notifications.objects.filter(event=event, user=self.user).exists())
