from django.db import models
from django.contrib.auth.models import User
from django.db.models.functions import Now
from django.utils import timezone
from .models import Event, Notifications, UnavailableSlot, isTimeAvailable
from django.core.exceptions import ValidationError

import datetime

#superuser : porta pw : (lowercase)(default one)

class Event(models.Model):
    # contains title, desc, start/end time vars, etc for the event
    title = models.CharField(max_length=150, default="My Event")
    description = models.TextField(blank=True)
    start_time = models.DateTimeField(default=timezone.now)
    end_time = models.DateTimeField(default= lambda: timezone.now() + datetime.timedelta(hours=1))
    user_created = models.ForeignKey(User, on_delete=models.CASCADE, null=True) 
    attendee = models.ManyToManyField(User, related_name='events', blank=True)
    location= models.CharField(max_length=200, null=True)


    def __str__(self):
        return self.title # string of event 
    
class Notifications(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    time_sent = models.DateTimeField(auto_now_add=True) 
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} about {self.event.title}'



class UnavailableSlot(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()

    RECURRENCE_CHOICES = [
        ('None', 'None'),
        ('Daily', 'Daily'),
        ('Weekly', 'Weekly')
    ]
    recurrence = models.CharField(
        max_length=20,
        choices=RECURRENCE_CHOICES,
        default='None'
    )
    description = models.CharField(max_length=255, blank=True, null=True)

    def is_active(self):
        return self.end_time >= timezone.now()

    def clean(self):
        if not isTimeAvailable(self.user, self.start_time, self.end_time):
            raise ValidationError("This time slot overlaps with an existing blocked slot.")

    def save(self, *args, **kwargs):
        self.clean() 
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.user} - {self.start_time.strftime('%Y-%m-%d %H:%M')} to {self.end_time.strftime('%Y-%m-%d %H:%M')} ({self.recurrence})"

