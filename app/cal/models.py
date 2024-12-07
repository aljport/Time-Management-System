from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.utils import timezone
from users.models import Profile, Friends

import datetime


<!-- contains title, desc, start/end time vars, etc for the event -->
class Event(models.Model):
    title = models.CharField(max_length=150, default="My Event")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default= timezone.now() + datetime.timedelta(hours=1))
    user_created = models.ForeignKey(Profile, on_delete=models.CASCADE, null=True, related_name='created_events')
    id = models.AutoField(primary_key=True)
    attendee = models.ManyToManyField(Profile, related_name='events', blank=True)
    location= models.CharField(max_length=200, null=True)


    def __str__(self):
        return self.title <!-- string of event  --> 
    
class Notifications(models.Model):
    <!-- links both event and user who get notif / what notif is  --> 
    event = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(Event, on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now_add=True) 
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} about {self.event.title}'  
