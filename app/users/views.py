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
        profile = Profile(user = user, isViewer = False)


        user.save()
        profile.save()

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
        user.profile.save()
        return redirect ('/users/password_confirm')
        
    return render(request, 'password_change.html')

def password_confirm_page(request):
    return render(request, 'password_confirm.html')
        
def account_information_page(request):
    if request.method == 'POST':
        logout(request)
        return redirect('/users/login')
    
    if not request.user.is_authenticated:
        return render(request, 'account_information.html')
    
    username = request.user.username
    name = request.user.get_full_name()
    email = request.user.email
    return render(request, 'account_information.html', {'username' : username, 'name' : name, 'email' : email})

def friend_list_page(request):
    if request.method == 'POST':
        friend_username = request.POST.get('username')

        if friend_username == request.user.username:
            messages.error(request, 'You can not have yourself as a friend')
            return redirect('/users/friend_list')

        if not User.objects.filter(username = friend_username).exists():
            messages.error(request, 'User does not exist')
            return redirect('/users/friend_list')
        
        if request.user.profile.friendList.filter(Amigo = friend_user).exists():
            if request.user.profile.friendList.filter(Amigo = friend_user).first().viewable:
                messages.error(request, 'You are waiting for a response to your friend request to this person')
                return redirect('/users/friend_list')
            messages.error(request, 'You have already added this person as a friend')
            return redirect('/users/friend_list')

        
        #Send a email to the user being befriended before adding them to the friend list
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
    
    user_profile = request.user.profile
    return render(request, 'friend_list.html', {'friends' : user_profile.friendList.all})

def update_friendList(request, friend_id):
    profile = get_object_or_404(Profile, user=request.user)
    friend = get_object_or_404(Friends, id=friend_id)

    friend_user = friend.Amigo
    friend_profile = get_object_or_404(Profile, user=friend_user)
    friend_friend = friend_profile.friendList.filter(Amigo=request.user).first()

    if friend not in profile.friendList.all():
        return JsonResponse({'status': 'error', 'message': 'This is not your friend.'})
    
    
    action = request.POST.get('action')

    if action == "accept_request":
        friend.requestPending = False
        friend_friend.viewable = True
        friend.save()
        friend_friend.save()

        message = "Friend request accepted."
    elif action == "reject_request":
        profile.friendList.remove(friend)
        friend_profile.friendList.remove(friend_friend)

        message = "Friend request rejected."
    else:
        message = "Invalid action."

    return JsonResponse({'status': 'success', 'message': message})
