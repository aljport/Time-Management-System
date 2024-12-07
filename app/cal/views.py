from django.http import HttpResponse, Http404
from django.template import loader

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm, AttendeeForm, EditEventForm
from .models import User, Notifications 
from .utilities import save_user
from django.utils import timezone
from .forms import EventForm
from django.http import JsonResponse
from django.views.generic.edit import UpdateView
from .models import Event
from .date_get import getOffset, getNextOffset, get_week_range, getNextMonth, getNextMonthName, getNextOffsetDate, getPreviousMonth, getPreviousMonthName

import datetime
import calendar
import json


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
  


@login_required(login_url='/users/login')
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

@login_required(login_url='/users/login')
def weekview(request, month_date=int(datetime.datetime.now().strftime('%m')), 
               day_date=int(datetime.datetime.now().strftime('%d')), 
               year_date=int(datetime.datetime.now().strftime('%Y'))):

  hour_num = list(range(0, 24))
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
  specific_date = datetime.datetime(year_date, month_date, day_date)
  start_of_week = specific_date - datetime.timedelta(days=(specific_date.weekday() + 1) % 7)
  end_of_week = start_of_week + datetime.timedelta(days=7)
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


  #Mini Calendar
  #Get current date
  now = datetime.datetime.now()
  first_day_of_month = now.replace(day=1)
  weekday_name = first_day_of_month.strftime('%A')
  current_month_value = int(now.strftime('%m'))
  current_day_value = int(now.strftime('%d'))
  current_year_value = int(now.strftime('%Y'))
  current_month_days = calendar.monthrange(current_year_value, current_month_value)[1]
  month_days = list(range(1, current_month_days + 1))
  start_date = datetime.date(current_year_value, current_month_value, current_day_value)
  prev_month = getPreviousMonth(start_date)
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_value = prev_month.strftime('%m')
  next_month = getNextMonth(start_date, current_month_days)
  next_month_value = next_month.strftime('%m')
  offset = getOffset(weekday_name)
  last_day = start_date.replace(day=current_month_days)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))
  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))
  #end of mini calendar

  if int(start_month_value) == current_month_value:
     today_is_true = True
  else:
     today_is_true = False

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
  
  week_events = current_user_events.filter(start_time__lt=end_of_week, end_time__gte=start_of_week)

  context = {
    "start_of_week" : start_of_week,
    "end_of_week" : end_of_week,
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
    "events" : week_events,
    "current_user" : current_user,
    "today_is_true" : today_is_true,
    
    "month_days_list" : month_days,
    "day_offset" : offset,
    "month_events" : month_events,
    "next_month_events" : next_month_events,
    "prev_month_events" :prev_month_events,
    "next_offset" : next_offset,
    "next_offset_nums" : next_offset_nums,
    "current_days" : current_month_days,
  }

  return render(request, "calendar/weekviewer.html", context)

@login_required(login_url='/users/login')
def eventweekcard(request, month_date=int(datetime.datetime.now().strftime('%m')), 
               day_date=int(datetime.datetime.now().strftime('%d')), 
               year_date=int(datetime.datetime.now().strftime('%Y')), event_id = Event.objects.first()):

  hour_num = list(range(0, 24))
  day_names = ["SUN", "MON", "TUE", "WED", "THU", "FRI", "SAT"]
  specific_date = datetime.datetime(year_date, month_date, day_date)
  start_of_week = specific_date - datetime.timedelta(days=(specific_date.weekday() + 1) % 7)
  end_of_week = start_of_week + datetime.timedelta(days=7)
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


  #Mini Calendar
  #Get current date
  now = datetime.datetime.now()
  first_day_of_month = now.replace(day=1)
  weekday_name = first_day_of_month.strftime('%A')
  current_month_value = int(now.strftime('%m'))
  current_day_value = int(now.strftime('%d'))
  current_year_value = int(now.strftime('%Y'))
  current_month_days = calendar.monthrange(current_year_value, current_month_value)[1]
  month_days = list(range(1, current_month_days + 1))
  start_date = datetime.date(current_year_value, current_month_value, current_day_value)
  prev_month = getPreviousMonth(start_date)
  prev_date = calendar.monthrange(prev_month.year, prev_month.month)[1]
  prev_month_value = prev_month.strftime('%m')
  next_month = getNextMonth(start_date, current_month_days)
  next_month_value = next_month.strftime('%m')
  offset = getOffset(weekday_name)
  last_day = start_date.replace(day=current_month_days)
  offset_nums = list(range( prev_date - int(offset) + 1, prev_date + 1))
  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))
  #end of mini calendar

  if start_month_value == current_month_value:
    today_is_true = True
  else:
    today_is_true = False

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)

  week_events = current_user_events.filter(start_time__lt=end_of_week, end_time__gte=start_of_week)

  selected_event = current_user_events.filter(pk=event_id)
  my_event = selected_event.first()
  
  context = {
    "start_month_dates" : 11,
    "start_day_date" : start_day_value,  
    "start_year_date": start_year_value,
    "start_of_week" : start_of_week,
    "end_of_week" : end_of_week,
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
    "events" : week_events,
    "selected_event" : my_event,
    "current_user" : current_user,
    "today_is_true" : today_is_true,
    
  }

  return render(request, "calendar/eventweekcard.html", context)

@login_required(login_url='/users/login')
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

  next_month_value = next_month.strftime('%m')
  next_day_value = next_month.strftime('%d')
  next_year_value = next_month.strftime('%Y')

  last_day = start_date.replace(day=current_month_days)

  next_offset = getNextOffsetDate(last_day.strftime('%A'))
  next_offset_nums = list(range(1, next_offset + 1 ))

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)


  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]
  
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
    "month_days_list" : days,
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
    "current_user" : current_user,
    "todo_events" : todo_events,
  }

  return render(request, "calendar/monthviewer.html", context)

@login_required(login_url='/users/login')
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

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)

  current_day_event = current_user_events.filter(start_time__date__lte=datetime.datetime(year_date, month_date, selected_day),end_time__date__gte=datetime.datetime(year_date, month_date, selected_day))

  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]

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
    "current_user" : current_user,
    "todo_events" : todo_events,
    "month_days_list" : days,
  }
  return render(request, "calendar/monthevent.html", context)

@login_required(login_url='/users/login')
def eventmonthcard(request, month_date, day_date, year_date, event_id):
   
  #passed in Information
  start_month_date = month_date
  start_day_date = day_date
  start_year_date =  year_date
  selected_day=int(datetime.datetime.now().strftime('%d'))
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


  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)

  selected_event = current_user_events.filter(pk=event_id)
  my_event = selected_event.first()

  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]

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
    "month_events" :month_events,
    "next_month_events" : next_month_events,
    "prev_month_events" :prev_month_events,
    "selected_event" : my_event,
    "id" : event_id,
    "current_user" : current_user,
    "selected_day" : selected_day,
    "todo_events" : todo_events,
    "month_days_list" : days,
  }

  return render(request, "calendar/eventcardmonthdefault.html", context)

@login_required(login_url='/users/login')
def create_event_card(request, month_date=int(datetime.datetime.now().strftime('%m')), 
                day_date=int(datetime.datetime.now().strftime('%d')), 
                year_date=int(datetime.datetime.now().strftime('%Y')), selected_day=int(datetime.datetime.now().strftime('%d'))):

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

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)

  current_day_event= current_user_events.filter(start_time__month=month_date, start_time__day=selected_day)
  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  if request.method == "POST":
        form = EventForm(request.POST)
        if form.is_valid():
            event = form.save(commit=False)
            event.user_created = request.user.profile  # Set the user who created the event
            event.save()  # Save the event to the database
            return redirect(f'/cal/month/{month_date}/{day_date}/{year_date}/{selected_day}')
  else:
      form = EventForm()

  rendered_form = form.render("calendar/month_event_format.html")

  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]
  
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
    "current_user" : current_user,
    "month_days_list" : days,
    "todo_events" : todo_events,
  }

  return render(request, "calendar/eventcreatecard.html", context)

@login_required(login_url='/users/login')
def editevent(request, month_date, day_date, year_date, event_id, selected_day=int(datetime.datetime.now().strftime('%d'))):
   

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

  current_user = request.user
  current_user_events = current_user.profile.created_events.all()

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  current_user_events = (current_user_events | attending_events).distinct()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)

  current_day_event = current_user_events.filter(start_time__date__lte=datetime.datetime(year_date, month_date, selected_day),end_time__date__gte=datetime.datetime(year_date, month_date, selected_day))
  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  #Week Information

  event = get_object_or_404(Event, pk=event_id)
  if request.method == "POST":
    form = EditEventForm(request.POST, instance=event)
    if form.is_valid():
        form.save()
        return redirect(f'/cal/month/{month_date}/{day_date}/{year_date}/event/{event_id}')
  else:
    print("Not Post")
    form = EditEventForm(instance=event)
  
  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]
  #rendered_form = form.render("calendar/month_event_format.html")

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
    "current_day_event" : current_day_event,
    "form" : form,
    "current_user" : current_user,
    "month_days_list" : days,
    "todo_events" : todo_events,
  }


  return render(request, "calendar/editevent.html", context)

@login_required(login_url='/users/login')
def modifyattendees(request, month_date, day_date, year_date, event_id, selected_day=int(datetime.datetime.now().strftime('%d'))):
   
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

  #gets current logged in user
  current_user = request.user
  current_user_events = current_user.profile.created_events.all()
  attending_events = current_user.profile.events.all()
  todays_events = current_user_events.filter(start_time__month=month_date, start_time__day=day_date)
  month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
  month_attending_events = attending_events.filter(start_time__month=month_date, start_time__year=year_date)
  month_events = (month_events | month_attending_events).distinct()
  next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  next_month_attending_events = attending_events.filter(start_time__month=next_month_value, start_time__year=year_date)
  next_month_events = (next_month_events | next_month_attending_events).distinct()
  prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
  prev_month_attending_events = attending_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
  prev_month_events = (prev_month_events | prev_month_attending_events).distinct()

  current_day_event = current_user_events.filter(start_time__date__lte=datetime.datetime(year_date, month_date, selected_day),end_time__date__gte=datetime.datetime(year_date, month_date, selected_day))
  selected_day_event = datetime.date(start_year_date, start_month_date, selected_day)

  selected_event = current_user_events.filter(pk=event_id)
  my_event = selected_event.first()

  event = get_object_or_404(Event, pk=event_id)
  if request.method == "POST":
        form = AttendeeForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            form.save()
            return redirect(f'/cal/month/{month_date}/{day_date}/{year_date}/event/{event_id}')
  else:
      form = AttendeeForm(instance=event, user=request.user)
  
  rendered_form = form.render("calendar/attendees_form.html")

  my_todo_events = month_events.filter(start_time__day=day_date)
  todo_events = my_todo_events[:5]

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
    "current_day_event" : current_day_event,
    "form" : form,
    "current_user" : current_user,
    "selected_event" : my_event,
    "month_days_list" : days,
    "todo_events" : todo_events,
  }

  return render(request, "calendar/modifyattendees.html", context)


def agendaview(request):

  if request.user.is_authenticated:
    # Do something for authenticated users.
    print("User Logged In!")
  else:
    # Do something for anonymous users.
    print("User Not Logged In!")
  current_user = request.user

  current_user_events = current_user.profile.created_events.all()

  context ={
    "user_events": current_user_events,
    "current_user" : current_user,
  }
   
  return render(request, "calendar/agendaview.html", context)


@login_required(login_url='/users/login')
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

# creates the notification for the user creating the event 
def create_notifications(event, attendees):
    notifications = [   
        Notifications(event=event, user=attendee)
        for attendee in attendees
    ]
    Notifications.objects.bulk_create(notifications)

# handles post request to change the status of a meeting 
# updates meeting and sends notification to participants
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


# verify request and retrives the request data 
# validate date and time format and that attendee exists
# check if time is available 
# create meeting
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
        
# blocks time slot after verifying that it is able to be blocked/ meeting is able to be created 
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

        end_time = start_time + datetime.timedelta(minutes=duration)

        if isTimeAvailable(user, start_time, end_time):
            try:
                UnavailableSlot.objects.create(user=user, start_time=start_time, end_time=end_time)
                return JsonResponse({'status': 'success', 'message': 'Time slot blocked successfully.'})
            except ValidationError as e:
                return JsonResponse({'status': 'error', 'message': str(e)})
        else:
            return JsonResponse({'status': 'error', 'message': 'The selected time slot overlaps with an existing blocked slot.'})
    return JsonResponse({'status': 'error', 'message': 'Invalid request method.'})
