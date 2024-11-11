from django import forms
from .models import Event

class EventForm(forms.ModelForm):
    class Meta:
        model = Event 
        fields = ['title', 'start_time', 'end_time', 'location', 'description']
        template_name = "calendar/month_event_format.html"
