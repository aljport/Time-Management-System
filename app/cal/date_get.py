from django.http import HttpResponse, Http404
from django.template import loader

from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect, get_object_or_404
from .models import Event
from .forms import EventForm
from .models import User, Notifications 
from .utilities import save_user
from django.utils import timezone


import datetime
import calendar


from .models import User


#Helper functions
def getOffset(day_name):
  if day_name == 'Sunday':
    return 0
  elif day_name == 'Monday':
    return 1
  elif day_name == 'Tuesday':
    return 2
  elif day_name == 'Wednesday':
    return 3
  elif day_name == 'Thursday':
    return 4
  elif day_name == 'Friday':
    return 5
  else:
    return 6
  
def getNextOffset(day_name):
  if day_name == 'Sunday':
    return 6
  elif day_name == 'Monday':
    return 5
  elif day_name == 'Tuesday':
    return 4
  elif day_name == 'Wednesday':
    return 3
  elif day_name == 'Thursday':
    return 2
  elif day_name == 'Friday':
    return 1
  else:
    return 0
  
def getPreviousMonth(date):
  today = date
  first = today.replace(day=1)
  last_month = first - datetime.timedelta(days=1)
  return last_month

def getPreviousMonthName(date):
  today = date
  first = today.replace(day=1)
  last_month = first - datetime.timedelta(days=1)
  return last_month.strftime("%B")


def getNextMonth(date, last_day):
  today = date
  first = today.replace(day=last_day)
  next_month = first + datetime.timedelta(days=1)
  return next_month

def getNextMonthName(date, last_day):
  today = date
  first = today.replace(day=last_day)
  next_month = first + datetime.timedelta(days=1)
  return next_month.strftime("%B")

def getNextOffsetDate(day_name):
  if day_name == "Sunday":
    return 6
  elif day_name == 'Monday':
    return 5
  elif day_name == 'Tuesday':
    return 4
  elif day_name == 'Wednesday':
    return 3
  elif day_name == 'Thursday':
    return 2
  elif day_name == 'Friday':
    return 1
  else:
    return 0

def get_week_range(date):
  # Find the day of the week (0 = Monday, 6 = Sunday)
  # Adjust so that Sunday is the first day (0 = Sunday, 6 = Saturday)
  start_of_week = date - datetime.timedelta(days=(date.weekday() + 1) % 7)  # Get the Sunday of the week
  end_of_week = start_of_week + datetime.timedelta(days=6)                  # Get the Saturday of the week
  return start_of_week