from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.utils import timezone

import datetime

#superuser : porta pw : (lowercase)(default one)

class Event(models.Model):
    # contains title, desc, start/end time vars, etc for the event
    title = models.CharField(max_length=150, default="My Event")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default= timezone.now() + datetime.timedelta(hours=1))
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    attendee = models.ManyToManyField(User, related_name='events', blank=True)
    location= models.CharField(max_length=200, null=True)
    id = models.AutoField(primary_key=True)


    def __str__(self):
        return self.title # string of event 
    
class Notifications(models.Model):
    # links both event and user who get notif / what notif is 
    event = models.ForeignKey(User, on_delete=models.CASCADE)
    user = models.ForeignKey(Event, on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now_add=True) 
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} about {self.event.title}'  
