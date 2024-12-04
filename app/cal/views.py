from django.http import HttpResponse, Http404
from django.template import loader
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils import timezone
from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from django.core.mail import send_mail
from .forms import EventForm
from .models import User, Notifications 
from .utilities import isTimeAvailable
from .forms import EventForm
from .models import Event, Notifications, UnavailableSlot
from django.http import JsonResponse
from .date_get import getOffset, getNextOffset, get_week_range, getNextMonth, getNextMonthName, getNextOffsetDate, getPreviousMonth, getPreviousMonthName

import datetime
import calendar


from .models import User

#we will need a view start to determine when to render calendar
  
def getPrevMonth():
  today = datetime.datetime.today()
  first = today.replace(day=1)
  last_month = first - datetime.timedelta(days=1)
  return last_month

def getPrevMonthName():
  today = datetime.datetime.today()
  first = today.replace(day=1)
  last_month = first - datetime.timedelta(days=1)
  return last_month.strftime("%B")
  
def index(request):
  
  current_month_name = datetime.datetime.today().strftime("%B")

  prev_month_value = 1
  prev_day_value = 1
  prev_year_value = 2024

  context = {
    "current_month" : current_month_name,
    "prev_month_value" : prev_month_value,
    "prev_day_value" : prev_day_value,
    "prev_year_value" : prev_year_value,

  }
  return render(request, "calendar/base.html", context)


def weekview(request, month_date=int(datetime.datetime.now().strftime('%m')), 
               day_date=int(datetime.datetime.now().strftime('%d')), 
               year_date=int(datetime.datetime.now().strftime('%Y'))):

  hour_num = list(range(0, 24))
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
  specific_date = datetime.datetime(year_date, month_date, day_date)
  start_of_week = specific_date - datetime.timedelta(days=(specific_date.weekday() + 1) % 7)
  start_month_value = start_of_week.strftime('%m')
  start_day_value = start_of_week.strftime('%d')
  start_year_value = start_of_week.strftime('%Y')

  first_date = get_week_range(specific_date)
  current_month_name = datetime.datetime.today().strftime("%B") 


  #Checks if it is the current date
  now = datetime.datetime.now()
  current_month_value = now.strftime('%m')
  current_day_value = now.strftime('%d')
  current_year_value = now.strftime('%Y')
  current_day_name = datetime.datetime.today().strftime("%A")
  days = [int((start_of_week + datetime.timedelta(days=i)).strftime('%d')) for i in range(7)]

  next_week_start = start_of_week + datetime.timedelta(days=7)
  next_week_day = next_week_start.strftime('%d')
  next_week_month = next_week_start.strftime('%m')
  next_week_year = next_week_start.strftime('%Y')

  prev_week_end = start_of_week - datetime.timedelta(days=1)
  prev_week_date = prev_week_end.strftime('%d')
  prev_week_month = prev_week_end.strftime('%m')
  prev_week_year = prev_week_end.strftime('%Y')

  context = {
    "current_month_value" : current_month_value,
    "current_day_value" : current_day_value,
    "current_year_value" : current_year_value,
    "day_names" : day_names,
    "day_nums" : days,
    "hours" : hour_num,
    "today_date" : timezone.now().day,
    "today_name"  : current_day_name,
    "first" : first_date,
    "current_month" : current_month_name,
    "next_week_day" : next_week_day,
    "next_week_month" : next_week_month,
    "next_week_year" : next_week_year,
    "prev_week_day" : prev_week_date,
    "prev_week_month" : prev_week_month,
    "prev_week_year" : prev_week_year,
    "prev_date" : prev_week_end.strftime('%d'),
    "start_month_value" : start_month_value,
    "start_day_value" : start_day_value,
    "start_year_value" : start_year_value,
  }

  return render(request, "calendar/weekviewer.html", context)


def monthviewer(request, month_date=int(datetime.datetime.now().strftime('%m')), 
                day_date=int(datetime.datetime.now().strftime('%d')), 
                year_date=int(datetime.datetime.now().strftime('%Y'))):

  #passed in Information
  start_month_date = month_date
  start_day_date = day_date
  start_year_date =  year_date

  start_date = datetime.date(start_year_date, start_month_date, start_day_date)
  first_day_of_month = start_date.replace(day=1)
  weekday_name = first_day_of_month.strftime('%A')
  start_month_name = start_date.strftime('%B')

  start_month_value = start_date.strftime('%m')
  start_day_value = start_date.strftime('%d')
  start_year_value = start_date.strftime('%Y')

  start_month_abv = start_date.strftime('%b')

  current_month_days = calendar.monthrange(start_year_date, start_month_date)[1]
  days = list(range(1, current_month_days + 1))

  #Get current date
  now = datetime.datetime.now()
  current_month = now.strftime('%B')
  current_month_value = now.strftime('%m')
  current_day_value = now.strftime('%d')
  current_year_value = now.strftime('%Y')

  
  #List of days in the week
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

  prev_month = getPreviousMonth(start_date)
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_name = getPreviousMonthName(start_date)

  prev_month_value = prev_month.strftime('%m')
  prev_day_value = prev_month.strftime('%d')
  prev_year_value = prev_month.strftime('%Y')

  #previous month offsets
  offset = getOffset(weekday_name)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))

  next_month = getNextMonth(start_date, current_month_days)
  next_date = calendar.monthrange(next_month.year, next_month.month)[1]
  next_month_date = getNextMonthName(start_date, current_month_days)

  next_month_value = next_month.strftime('%m')
  next_day_value = next_month.strftime('%d')
  next_year_value = next_month.strftime('%Y')

  last_day = start_date.replace(day=current_month_days)

  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))

  todays_events = Event.objects.filter(start_time__month=month_date, start_time__day=day_date)

  month_events = Event.objects.filter(start_time__month=month_date)

  next_month_events = Event.objects.filter(start_time__month=next_month_value)
  prev_month_events = Event.objects.filter(start_time__month=prev_month_value)


  context = {
    "start_month_date" : start_month_date,
    "start_day_date" : start_day_date,
    "start_year_date" : start_year_date,
    "start_month_abv" : start_month_abv,
    "start_month_name" : start_month_name,
    "current_month_value" : current_month_value,
    "current_day_value" : current_day_value,
    "current_year_value" : current_year_value,
    "start_month_value" : start_month_value,
    "start_day_value" : start_day_value,
    "start_year_value" : start_year_value,
    "day_names" : day_names,
    "weekday_name" : weekday_name,
    "prev_month_name": prev_month_name,
    "day_offset" : offset,
    "offset_numbers" : offset_nums,
    "days_list" : days,
    "date" : timezone.now().day,
    "current_month" : current_month,
    "current_days" : current_month_days,
    "next_offset" : next_offset,
    "next_offset_nums" : next_offset_nums,
    "next_month" : next_month,
    "prev_month_value" : prev_month_value,
    "prev_day_value" : prev_day_value,
    "prev_year_value" : prev_year_value,
    "next_month_value" : next_month_value,
    "next_day_value" : next_day_value,
    "next_year_value" : next_year_value,
    "todays_events" : todays_events,
    "month_events" :month_events,
    "next_month_events" : next_month_events,
    "prev_month_events" :prev_month_events,
  }

  return render(request, "calendar/monthviewer.html", context)

def monthview(request):
  current_day_name = datetime.datetime.today().strftime("%A")
  current_year = datetime.datetime.today().year
  current_month = datetime.datetime.today().month
  current_month_name = datetime.datetime.today().strftime("%B")
  current_month_days = calendar.monthrange(current_year, current_month)[1]
  days = list(range(1, current_month_days + 1))
  #days = list(range(1, 32))

  #List of days
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

  #Get current time
  timenow = timezone.now().strftime("%d/%m/%Y, %H:%M:%S")
  view_names = ["week", "month", "agenda"]

  #Get current date
  now = datetime.datetime.now()

  # Find the first day of the current month
  first_day_of_month = now.replace(day=1)
  # Get the name of the weekday for the first day of the month
  # The .strftime('%A') will return the full weekday name (e.g., "Monday")
  weekday_name = first_day_of_month.strftime('%A')

  prev_month = getPrevMonth()
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_name = getPrevMonthName()

  #previous month offsets
  offset = getOffset(weekday_name)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))

  month_days = 31
  total_days = list(range(1, month_days + offset + 1))

  next_offset = getNextOffset(current_month_days)
  next_offset_nums = list(range(1, offset + 1 ))


  context = {
    "days_list" : days,
    "day_names" : day_names,
    "current_days" : current_month_days,
    "time" : timenow,
    "views" : view_names,
    "date" : timezone.now().day,
    "day_name"  : current_day_name,
    "first_day" : weekday_name,
    "day_offset" : offset,
    "total_days" : total_days,
    "offset_numbers" : offset_nums,
    "next_offset" : next_offset,
    "next_offset_nums" : next_offset_nums,
    "current_month" : current_month_name,
    "prev_month" : prev_month_name,
    "prev_date" : prev_date,
    
  }
  return render(request, "calendar/monthview.html", context)


def monthevent(request, month_date, day_date, year_date, selected_day):

  #passed in Information
  start_month_date = month_date
  start_day_date = day_date
  start_year_date =  year_date

  start_date = datetime.date(start_year_date, start_month_date, start_day_date)
  first_day_of_month = start_date.replace(day=1)
  weekday_name = first_day_of_month.strftime('%A')
  start_month_name = start_date.strftime('%B')

  start_month_value = start_date.strftime('%m')
  start_day_value = start_date.strftime('%d')
  start_year_value = start_date.strftime('%Y')

  start_month_abv = start_date.strftime('%b')

  current_month_days = calendar.monthrange(start_year_date, start_month_date)[1]
  days = list(range(1, current_month_days + 1))

  #Get current date
  now = datetime.datetime.now()
  current_month = now.strftime('%B')
  current_month_value = now.strftime('%m')
  current_day_value = now.strftime('%d')
  current_year_value = now.strftime('%Y')
  #List of days in the week
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

  prev_month = getPreviousMonth(start_date)
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_name = getPreviousMonthName(start_date)

  prev_month_value = prev_month.strftime('%m')
  prev_day_value = prev_month.strftime('%d')
  prev_year_value = prev_month.strftime('%Y')

  #previous month offsets
  offset = getOffset(weekday_name)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))

  next_month = getNextMonth(start_date, current_month_days)
  next_date = calendar.monthrange(next_month.year, next_month.month)[1]
  next_month_date = getNextMonthName(start_date, current_month_days)

  next_month_value = next_month.strftime('%m')
  next_day_value = next_month.strftime('%d')
  next_year_value = next_month.strftime('%Y')

  last_day = start_date.replace(day=current_month_days)

  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))

  todays_events = Event.objects.filter(start_time__month=month_date, start_time__day=day_date)

  month_events = Event.objects.filter(start_time__month=month_date)

  next_month_events = Event.objects.filter(start_time__month=next_month_value)
  prev_month_events = Event.objects.filter(start_time__month=prev_month_value)

  current_day_event= Event.objects.filter(start_time__month=month_date, start_time__day=selected_day)

  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  

  context = {
    "selected_day" : selected_day,
    "start_date" : selected_day_event .strftime("%B %d, %Y"),
    "start_month_date" : start_month_date,
    "start_day_date" : start_day_date,
    "start_year_date" : start_year_date,
    "start_month_abv" : start_month_abv,
    "start_month_name" : start_month_name,
    "current_month_value" : current_month_value,
    "current_day_value" : current_day_value,
    "current_year_value" : current_year_value,
    "start_month_value" : start_month_value,
    "start_day_value" : start_day_value,
    "start_year_value" : start_year_value,
    "day_names" : day_names,
    "weekday_name" : weekday_name,
    "prev_month_name": prev_month_name,
    "day_offset" : offset,
    "offset_numbers" : offset_nums,
    "days_list" : days,
    "date" : timezone.now().day,
    "current_month" : current_month,
    "current_days" : current_month_days,
    "next_offset" : next_offset,
    "next_offset_nums" : next_offset_nums,
    "next_month" : next_month,
    "prev_month_value" : prev_month_value,
    "prev_day_value" : prev_day_value,
    "prev_year_value" : prev_year_value,
    "next_month_value" : next_month_value,
    "next_day_value" : next_day_value,
    "next_year_value" : next_year_value,
    "todays_events" : todays_events,
    "month_events" :month_events,
    "next_month_events" : next_month_events,
    "prev_month_events" :prev_month_events,
    "current_day_event" : current_day_event,


  }
  return render(request, "calendar/monthevent.html", context)


def create_event_card(request, month_date, day_date, year_date, selected_day):

  #passed in Information
  start_month_date = month_date
  start_day_date = day_date
  start_year_date =  year_date
  start_date = datetime.date(start_year_date, start_month_date, start_day_date)
  first_day_of_month = start_date.replace(day=1)
  weekday_name = first_day_of_month.strftime('%A')
  start_month_name = start_date.strftime('%B')
  start_month_value = start_date.strftime('%m')
  start_day_value = start_date.strftime('%d')
  start_year_value = start_date.strftime('%Y')
  start_month_abv = start_date.strftime('%b')
  current_month_days = calendar.monthrange(start_year_date, start_month_date)[1]
  days = list(range(1, current_month_days + 1))

  #Get current date
  now = datetime.datetime.now()
  current_month = now.strftime('%B')
  current_month_value = now.strftime('%m')
  current_day_value = now.strftime('%d')
  current_year_value = now.strftime('%Y')
  #List of days in the week
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]

  prev_month = getPreviousMonth(start_date)
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_name = getPreviousMonthName(start_date)
  prev_month_value = prev_month.strftime('%m')
  prev_day_value = prev_month.strftime('%d')
  prev_year_value = prev_month.strftime('%Y')

  #previous month offsets
  offset = getOffset(weekday_name)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))

  next_month = getNextMonth(start_date, current_month_days)
  next_month_value = next_month.strftime('%m')
  next_day_value = next_month.strftime('%d')
  next_year_value = next_month.strftime('%Y')
  last_day = start_date.replace(day=current_month_days)
  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))

  todays_events = Event.objects.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = Event.objects.filter(start_time__month=month_date)
  next_month_events = Event.objects.filter(start_time__month=next_month_value)
  prev_month_events = Event.objects.filter(start_time__month=prev_month_value)
  current_day_event= Event.objects.filter(start_time__month=month_date, start_time__day=selected_day)
  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_created = request.user  # Set the user who created the event
            event.save()  # Save the event to the database
            return redirect(f'/cal/month/{month_date}/{day_date}/{year_date}/{selected_day}')
  else:
      form = EventForm()

  rendered_form = form.render("calendar/month_event_format.html")

  
  context = {
    "start_date" : selected_day_event .strftime("%B %d, %Y"),
    "start_month_date" : start_month_date,
    "start_day_date" : start_day_date,
    "start_year_date" : start_year_date,
    "start_month_abv" : start_month_abv,
    "start_month_name" : start_month_name,
    "current_month_value" : current_month_value,
    "current_day_value" : current_day_value,
    "current_year_value" : current_year_value,
    "start_month_value" : start_month_value,
    "start_day_value" : start_day_value,
    "start_year_value" : start_year_value,
    "day_names" : day_names,
    "weekday_name" : weekday_name,
    "prev_month_name": prev_month_name,
    "day_offset" : offset,
    "offset_numbers" : offset_nums,
    "days_list" : days,
    "date" : timezone.now().day,
    "current_month" : current_month,
    "current_days" : current_month_days,
    "next_offset" : next_offset,
    "next_offset_nums" : next_offset_nums,
    "next_month" : next_month,
    "prev_month_value" : prev_month_value,
    "prev_day_value" : prev_day_value,
    "prev_year_value" : prev_year_value,
    "next_month_value" : next_month_value,
    "next_day_value" : next_day_value,
    "next_year_value" : next_year_value,
    "todays_events" : todays_events,
    "month_events" :month_events,
    "next_month_events" : next_month_events,
    "prev_month_events" :prev_month_events,
    "current_day_event" : current_day_event,
    "form" : rendered_form,

  }

  return render(request, "calendar/eventcreatecard.html", context)

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
    for attendee in attendees:
        # create the notification
        notification = Notifications.objects.create(event=event, user=attendee)

        # send email to person attending 
        send_mail(
            subject=f"New Event: {event.title}",
            message=f"You have been invited to the event '{event.title}' starting at {event.start_time}.",
            from_email='noreply@onschedule.com',  # replace with app email? 
            recipient_list=[attendee.email], #replace with the user email 
            fail_silently=False,
        )


def change_meeting_status(request):
    if request.method == 'POST':
        meeting_id = request.POST.get('meeting_id')
        new_status = request.POST.get('status')

        # acceptable status
        if new_status not in ['Accepted', 'Declined', 'Pending']:
            return JsonResponse({'status': 'error', 'message': 'Invalid status value.'})

        # error handling
        meeting = get_object_or_404(Event, id=meeting_id)
        meeting.status = new_status
        meeting.save()

        Notifications.objects.create(user=meeting.invitee, message=f"Your meeting request is {new_status}.")
        Notifications.objects.create(user=meeting.requester, message=f"Your meeting has been {new_status} by the invitee.")
        
        return JsonResponse({'status': 'success', 'message': 'Meeting status updated.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})

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

        # ensure start time is in the future 
        if start_time < timezone.now():
            return JsonResponse({'status': 'error', 'message': 'Start time must be in the future.'})

        # check if invitee exists 
        try:
            invitee = User.objects.get(id=invitee_id)
        except User.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Invitee does not exist.'})

        if isTimeAvailable(invitee_id, start_time, end_time):
            Event.objects.create(
                requester=requester,
                invitee=invitee,
                start_time=start_time,
                end_time=end_time
            )
            return JsonResponse({'status': 'success', 'message': 'Meeting request sent.'})
        else:
            return JsonResponse({'status': 'error', 'message': 'The requested time is not available.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
        

def block_time_slot(request):
    if request.method == 'POST':
        user = request.user
        start_time_str = request.POST.get('start_time')
        duration = request.POST.get('duration')

        try:
            # positive integer only
            duration = int(duration)
            if duration <= 0:
                raise ValueError('Duration must be a positive number.')

            start_time = timezone.make_aware(datetime.strptime(start_time_str, '%Y-%m-%d %H:%M:%S'))
        except ValueError as e:
            return JsonResponse({'status': 'error', 'message': str(e)})

        end_time = start_time + timedelta(minutes=duration)

        if isTimeAvailable(user, start_time, end_time):
            try:
                UnavailableSlot.objects.create(user=user, start_time=start_time, end_time=end_time)
                return JsonResponse({'status': 'success', 'message': 'Time slot blocked successfully.'})
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'The selected time slot overlaps with an existing blocked slot.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
