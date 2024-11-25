from django import forms
from .models import Event
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.exceptions import ValidationError
from .models import Event, Notifications, UnavailableSlot, isTimeAvailable

class EventForm(forms.ModelForm):
    start_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    start_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))
    end_date = forms.DateField(widget=forms.DateInput(attrs={'type': 'date'}))
    end_time = forms.TimeField(widget=forms.TimeInput(attrs={'type': 'time'}))

    class Meta:
        model = Event 
        fields = ['title', 'start_date', 'start_time', 'end_date', 'end_time', 'description', 'location']
        template_name = "calendar/month_event_format.html"

    def clean(self):
        cleaned_data = super().clean()
        start_date = cleaned_data.get("start_date")
        start_time = cleaned_data.get("start_time")
        end_date = cleaned_data.get("end_date")
        end_time = cleaned_data.get("end_time")

        if start_date and start_time:
            cleaned_data['start_time'] = timezone.make_aware(
                timezone.datetime.combine(start_date, start_time)
            )
        if end_date and end_time:
            cleaned_data['end_time'] = timezone.make_aware(
                timezone.datetime.combine(end_date, end_time)
            )

        # validate that end time is after start time
        if cleaned_data.get("start_time") and cleaned_data.get("end_time"):
            if cleaned_data["end_time"] <= cleaned_data["start_time"]:
                self.add_error("end_time", "End time must be after start time.")
        return cleaned_data
    

class BlockTimeSlotForm(forms.Form):
    start_time = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    duration = forms.IntegerField(min_value=15, max_value=60, help_text='Duration in minutes.')
    recurrence = forms.ChoiceField(choices=UnavailableSlot.RECURRENCE_CHOICES, required=False, initial='None')
    description = forms.CharField(max_length=255, required=False)

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)

    def clean_start_time(self):
        start_time = self.cleaned_data['start_time']
        if start_time < timezone.now():
            raise ValidationError("Start time cannot be in the past.")

        # check if slot is available 
        if self.user and not isTimeAvailable(self.user, start_time, start_time + datetime.timedelta(minutes=self.cleaned_data.get('duration', 0))):
            raise ValidationError("The selected time slot overlaps with an existing blocked time.")
        
        return start_time