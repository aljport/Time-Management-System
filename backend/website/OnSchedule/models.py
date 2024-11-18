from django.db import models
from django.contrib.auth.models import User

class Calendar_Event(models.Model):
    # contains title, desc, start/end time vars, etc for the event
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user_created = models.ForeignKey(User, on_delete=models.CASCADE) 
    attendee = models.ManyToManyField(User, related_name='events', blank=True)

    def __str__(self):
        return self.title # string of event 
    
class Notifications(models.Model):
    # links both event and user who get notif / what notif is 
    event = models.ForeignKey(Calendar_Event, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(Calendar_Event, on_delete=models.CASCADE, related_name='user_notifications')
    time_sent = models.DateTimeField(auto_now_add=True) 
    notified = models.BooleanField(default=False)

    def __str__(self):
        return f'Notification for {self.user.username} about {self.event.title}'  
    

