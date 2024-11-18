from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .forms import EventForm
from .models import User, Notifications 
from .utilities import save_user
from django.utils import timezone


def create_event(ev_req):
    if ev_req.method == 'POST':
        form = EventForm(ev_req.POST) 
        if form.is_valid():
            event = form.save(commit=False)
            event.user_created = ev_req.user
            event.save()
            return redirect('event_list')
        
        attendees = form.cleaned_data.get('attendee')
        if attendees:
            event.attendee.set(attendees)

        create_notifications(event, attendees)

    else:
        form = EventForm() # creates empty form 

    return render(ev_req, 'create_event.html', {'form': form})

def create_notifications(event, attendees):
    notifications = [   
        Notifications(event=event, user=attendee)
        for attendee in attendees
    ]
    Notifications.objects.bulk_create(notifications)
