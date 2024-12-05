from django import forms
from .models import Event
from django.utils import timezone
from django.views.generic.edit import UpdateView

from users.models import Profile

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

        # Validate that end time is after start time
        if cleaned_data.get("start_time") and cleaned_data.get("end_time"):
            if cleaned_data["end_time"] <= cleaned_data["start_time"]:
                self.add_error("end_time", "End time must be after start time.")
        return cleaned_data

class AttendeeForm(forms.ModelForm):
    attendee = forms.ModelMultipleChoiceField(
        queryset=Profile.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Attendees"
    )
    
    class Meta:
        model = Event
        fields = ['attendee']

class EditEventForm(forms.ModelForm):

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

        # Validate that end time is after start time
        if cleaned_data.get("start_time") and cleaned_data.get("end_time"):
            if cleaned_data["end_time"] <= cleaned_data["start_time"]:
                self.add_error("end_time", "End time must be after start time.")
        return cleaned_data
