from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import *
import random
from .models import Friends, Profile
from django.http import JsonResponse

from django.utils import timezone
import datetime
import calendar

from cal.date_get import getOffset, getNextOffset, get_week_range, getNextMonth, getNextMonthName, getNextOffsetDate, getPreviousMonth, getPreviousMonthName

RESET_PASSWORD_USERNAME = ""
NUMBER = ""
CURRENT_USER = None

# Create your views here.
def index(request):
    return render(request, 'home.html')

# Logs into the system with the designated username and password of the user
def login_page(request):
    global CURRENT_USER
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')
    
        if not User.objects.filter(username = username).exists():
            messages.error(request, 'Invalid Username')
            return redirect('/users/login')
    
        user = authenticate(username = username, password = password)

        if user is None:
            messages.error(request, "Invalid Password")
            return redirect('/users/login')
        else:
            login(request, user)
            CURRENT_USER = user
            CURRENT_USER.profile.isViewer = False
            return redirect('/cal/month') #replace with entrance to calander
        
    return render(request, 'login.html')

# Takes the information that was given in the page and turns it into a new user
def register_page(request):
    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = User.objects.filter(username = username)

        if user.exists():
            messages.info(request, "Username Invalid")
            return redirect('/users/register')
    
        user = User.objects.create_user(first_name = first_name, last_name = last_name, email = email, username = username, password = password)
        profile = Profile(user = user, isViewer = False)


        user.save()
        profile.save()

        messages.info(request, "Account Created")
        return redirect('/users/login')
    
    return render(request, 'register.html')

# Gets the username of the account they want to reset their password in
def username_get_page(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        
        user = User.objects.filter(username = username)

        if not user.exists():
            messages.info(request, "User does not exist")
            return redirect('/users/username_get')
        else:
            user = User.objects.get(username = username)
            global RESET_PASSWORD_USERNAME
            RESET_PASSWORD_USERNAME = username
            return redirect('/users/password_reset')
    return render(request, 'username_get.html')

# Asks the user to take the code they got from their email and put it in here
def password_reset_page(request):
    global NUMBER 
    if request.method == 'POST':
        inserted_Number = request.POST.get('number')

        if inserted_Number == NUMBER:
            return redirect('/users/password_change')
        else:
            messages.error(request, "Not the correct number, new email is being sent")
            return redirect('/users/password_reset')

    # Sets up the code and sends the email
    NUMBER = ""
        
    for i in range(8):
        random_int = random.randint(0, 9)
        NUMBER += str(random_int)
        
    subject = "Password Reset"

    message = "Hello "
    message += User.objects.get(username = RESET_PASSWORD_USERNAME).get_full_name()
    message += "\n\nWe have recieved a request to reset your password \nHere is the code to so\n"
    message += NUMBER
    message += "\n\nThank you for using OnSchedule"

    email_from = settings.EMAIL_HOST_USER

    recipient = [User.objects.get(username = RESET_PASSWORD_USERNAME).email]

    send_mail(subject, message, email_from, recipient)

    return render(request, 'password_reset.html')

    
# Asks the user to put in the new password twice and moves on if it they were the same
def password_change_page(request):
    if request.method == 'POST':
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')
        
        if password != confirm_password:
            messages.info(request, "Not the Same Password, Try Again")
            return redirect('/users/password_change')
        
        user = User.objects.get(username = RESET_PASSWORD_USERNAME)

        user.set_password(password)
        user.save()
        user.profile.save()
        return redirect ('/users/password_confirm')
        
    return render(request, 'password_change.html')

# Shows a screen that shows that the password reset was sucessful
def password_confirm_page(request):
    return render(request, 'password_confirm.html')

# Shows off the user's account information and allows the user to logout 
def account_information_page(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/users/login')
    
    if not request.user.is_authenticated:
        return render(request, 'account_information.html')
    
    username = request.user.username
    name = request.user.get_full_name()
    email = request.user.email


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

    current_user = request.user 
    current_user_events = current_user.profile.created_events.all()
    attending_events = current_user.profile.events.all()
    month_date = current_month_value
    year_date = current_year_value
    month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
    month_attending_events = attending_events.filter(start_time__month=month_date, start_time__year=year_date)
    month_events = (month_events | month_attending_events).distinct()
    next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
    next_month_attending_events = attending_events.filter(start_time__month=next_month_value, start_time__year=year_date)
    next_month_events = (next_month_events | next_month_attending_events).distinct()
    prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
    prev_month_attending_events = attending_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
    prev_month_events = (prev_month_events | prev_month_attending_events).distinct()


    my_todo_events = month_events.filter(start_time__day=current_day_value)
    todo_events = my_todo_events[:5]
    user = request.user
    user_profile = request.user.profile
    context ={
        'username' : username, 
        'name' : name, 
        'email' : email,
        "current_user" : user,
        'friends' : user_profile.friendList.all,
        
        "todo_events" : todo_events,
        "offset_numbers" : offset_nums,
        "month_days_list" : month_days,
        "day_offset" : offset,
        "month_events" : month_events,
        "next_month_events" : next_month_events,
        "prev_month_events" :prev_month_events,
        "next_offset" : next_offset,
        "next_offset_nums" : next_offset_nums,
        "current_days" : current_month_days,
    }
    return render(request, 'account_information.html', context)

# Sets up the friend list to show off each of the user's friend and allowed the user to submit a username of another user to make them into a friend
def friend_list_page(request):
    global CURRENT_USER
    if request.method == 'POST':
        friend_username = request.POST.get('username')

        if friend_username == request.user.username:
            messages.error(request, 'You can not have yourself as a friend')
            return redirect('/users/friend_list')

        if not User.objects.filter(username = friend_username).exists():
            messages.error(request, 'User does not exist')
            return redirect('/users/friend_list')
        
        if request.user.profile.friendList.filter(Amigo__username=friend_username).exists():
            if request.user.profile.friendList.filter(Amigo__username=friend_username).first().viewable:
                messages.error(request, 'You are waiting for a response to your friend request to this person')
                return redirect('/users/friend_list')
            messages.error(request, 'You have already added this person as a friend')
            return redirect('/users/friend_list')

        
        # Sets up the friend objects for both the current user and the recieving user
        friend_user = User.objects.get(username = friend_username)
        new_friend = Friends.objects.create(Amigo = friend_user, requestPending = False, viewable = False)
        new_friend.save()
        user_profile = request.user.profile
        user_profile.friendList.add(new_friend)
        user_profile.save()

        newer_friend = Friends.objects.create(Amigo = request.user, requestPending = True, viewable = True)
        newer_friend.save()
        friend_user.profile.friendList.add(newer_friend)
        friend_user.profile.save()

        messages.info(request, "Friend has been added")
        return redirect('/users/friend_list')
    
    CURRENT_USER = request.user
    CURRENT_USER.profile.isViewer = True
    user_profile = request.user.profile


    username = request.user.username
    name = request.user.get_full_name()
    email = request.user.email

    user = request.user

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

    current_user = request.user 
    current_user_events = current_user.profile.created_events.all()
    attending_events = current_user.profile.events.all()
    month_date = current_month_value
    year_date = current_year_value
    month_events = current_user_events.filter(start_time__month=month_date, start_time__year=year_date)
    month_attending_events = attending_events.filter(start_time__month=month_date, start_time__year=year_date)
    month_events = (month_events | month_attending_events).distinct()
    next_month_events = current_user_events.filter(start_time__month=next_month_value, start_time__year=year_date)
    next_month_attending_events = attending_events.filter(start_time__month=next_month_value, start_time__year=year_date)
    next_month_events = (next_month_events | next_month_attending_events).distinct()
    prev_month_events = current_user_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
    prev_month_attending_events = attending_events.filter(start_time__month=prev_month_value, start_time__year=year_date)
    prev_month_events = (prev_month_events | prev_month_attending_events).distinct()



    my_todo_events = month_events.filter(start_time__day=current_day_value)
    todo_events = my_todo_events[:5]
    context = {
        'friends' : user_profile.friendList.all,
        'username' : username, 
        'name' : name, 
        'email' : email,
        "current_user" : user,
        "todo_events" : todo_events,

        "offset_numbers" : offset_nums,
        "month_days_list" : month_days,
        "day_offset" : offset,
        "month_events" : month_events,
        "next_month_events" : next_month_events,
        "prev_month_events" :prev_month_events,
        "next_offset" : next_offset,
        "next_offset_nums" : next_offset_nums,
        "current_days" : current_month_days,
    }
    return render(request, 'friend_list.html', context)

# Accepts the friend request and the friend object to correspond to it
def accept_friend(request, friend_username):
    
    friend = request.user.profile.friendList.get(Amigo__username=friend_username)

    if friend.requestPending:
        friend.requestPending = False
        currentUserFriend = friend.Amigo.profile.friendList.get(Amigo = request.user)
        currentUserFriend.viewable = True
        friend.save()
        currentUserFriend.save()
        
        messages.success(request, f"You are now friends with {friend.Amigo.first_name}!")
    else:
        messages.error(request, "This friend request has already been accepted.")
    
    # Redirect to the same page
    return redirect('/users/friend_list')

# Rejects the friend request by removing the friend object from both user
def reject_friend(request, friend_username):
    
    friend = request.user.profile.friendList.filter(Amigo__username=friend_username).first()
    currentUserFriend = friend.Amigo.profile.friendList.get(Amigo = request.user)
    friend.delete()
    currentUserFriend.delete()
    messages.success(request, "Friend request rejected.")

    return redirect('/users/friend_list')

# Updates who the viewer who is viewing the code is.
def update_friend(request, friend_username):
    global CURRENT_USER
    
    friend = request.user.profile.friendList.filter(Amigo__username=friend_username).first()
    CURRENT_USER = friend.Amigo
    friend.Amigo.profile.isViewer = True
    
    return redirect('/cal/month')  # Replace with the target page URL
