from django.db import models
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.utils import timezone
from datetime import datetime, timedelta
from calendar import monthrange
from django.core.exceptions import ValidationError


class calendarEvent(models.Model):
    title = models.CharField(max_length=150)
    description = models.TextField(blank=True)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    user_created = models.ForeignKey(User, on_delete=models.CASCADE) 
    attendee = models.ManyToManyField(User, related_name='events', blank=True)

    requester = models.ForeignKey(User, on_delete=models.CASCADE, related_name='requested_events')
    invitee = models.ForeignKey(User, on_delete=models.CASCADE, related_name='invited_events')

    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Accepted', 'Accepted'),
        ('Declined', 'Declined')
    ]
    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default='Pending'
    )

    def __str__(self):
        return self.title
    
class Notifications(models.Model):

    # links both event and user who gets notification
    event = models.ForeignKey(calendarEvent, on_delete=models.CASCADE, related_name='notifications')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='user_notifications')  
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
    

def change_meeting_status(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        new_status = request.POST.get('status')

        meeting = calendarEvent.objects.get(id=meeting_id)
        meeting.status = new_status
        meeting.save()

        Notifications.objects.create(user=meeting.invitee, message=f"Your meeting request is {new_status}.")
        Notifications.objects.create(user=meeting.requester, message=f"Your meeting has been {new_status} by the invitee.")    


def request_meeting(request):
    if request.method == 'POST':
        requester = request.user
        invitee_id = request.POST.get('invitee_id')
        start_time = request.POST.get('start_time')
        end_time = request.POST.get('end_time')

        try:
            start_time = timezone.make_aware(datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S'))
            end_time = timezone.make_aware(datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid datetime format. Use YYYY-MM-DD HH:MM:SS'})

        if isTimeAvailable(invitee_id, start_time, end_time):
            calendarEvent.objects.create(
                requester=requester,
                invitee_id=invitee_id,
                start_time=start_time,
                end_time=end_time
            )
            return JsonResponse({'status': 'success', 'message': 'Meeting request sent.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'The requested time is not available.'})
        
def isTimeAvailable(user, start_time, end_time):
    conflicting_slot = UnavailableSlot.objects.filter(
        user=user,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exists()

    recurring_conflict = UnavailableSlot.objects.filter(
        user=user,
        recurrence__in=['Daily', 'Weekly'],
        start_time__time__lte=start_time.time(),
        end_time__time__gte=end_time.time()
    ).exists()

    return not (conflicting_slot or recurring_conflict)


def block_time_slot(request):
    if request.method == 'POST':
        user = request.user
        start_time_str = request.POST.get('start_time')
        duration = int(request.POST.get('duration')) 
        
        try:
            start_time = timezone.make_aware(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S'))
        except ValueError:
            return JsonResponse({'status': 'error', 'message': 'Invalid start time format. Use YYYY-MM-DD HH:MM:SS'})

        end_time = start_time + timedelta(minutes=duration)

        # check if the time slot is available before blocking it out 
        if isTimeAvailable(user, start_time, end_time):
            try:
                UnavailableSlot.objects.create(user=user, start_time=start_time, end_time=end_time)
                return JsonResponse({'status': 'success', 'message': 'Time slot blocked successfully.'})
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'The selected time slot overlaps with an existing blocked slot.'})
    else:
        return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
    
def create_recurring_unavailable_slots(self, recurrence, start_time, end_time):
    
    if recurrence == 'Daily':
        for i in range(7):  
            new_start_time = start_time + timedelta(days=i)
            new_end_time = end_time + timedelta(days=i)
            UnavailableSlot.objects.create(user=self.user, start_time=new_start_time, end_time=new_end_time, recurrence=recurrence)
    elif recurrence == 'Weekly':
        for i in range(4):  
            new_start_time = start_time + timedelta(weeks=i)
            new_end_time = end_time + timedelta(weeks=i)
            UnavailableSlot.objects.create(user=self.user, start_time=new_start_time, end_time=new_end_time, recurrence=recurrence)
    elif recurrence == 'Monthly':
        for i in range(12):
           
            month = (start_time.month + i) % 12
            year = start_time.year + ((start_time.month + i) // 12)
            
          
            try:
                new_start_time = start_time.replace(year=year, month=month, day=start_time.day)
                new_end_time = end_time.replace(year=year, month=month, day=end_time.day)
            except ValueError:
                
                last_day_of_month = monthrange(year, month)[1]
                new_start_time = start_time.replace(year=year, month=month, day=last_day_of_month)
                new_end_time = end_time.replace(year=year, month=month, day=last_day_of_month)

            UnavailableSlot.objects.create(user=self.user, start_time=new_start_time, end_time=new_end_time, recurrence=recurrence)