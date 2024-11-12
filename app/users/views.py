from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.core.mail import send_mail
from django.conf import settings
from .models import *
import random

RESET_PASSWORD_USERNAME = ""
NUMBER = ""

# Create your views here.
def index(request):
    return render(request, 'home.html')

def login_page(request):
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
            return redirect('/cal/month') #replace with entrance to calander
        
    return render(request, 'login.html')

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

        user.save()

        messages.info(request, "Account Created")
        return redirect('/users/login')
    
    return render(request, 'register.html')

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


def password_reset_page(request):
    global NUMBER 
    if request.method == 'POST':
        inserted_Number = request.POST.get('number')

        if inserted_Number == NUMBER:
            return redirect('/users/password_change')
        else:
            messages.error(request, "Not the correct number, new email is being sent")
            return redirect('/users/password_reset')

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
        return redirect ('/users/password_confirm')
        
    return render(request, 'password_change.html')

def password_confirm_page(request):
    return render(request, 'password_confirm.html')
        

