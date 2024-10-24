from django.contrib.auth.forms import UserCreationForm
from django.shortcuts import render, redirect
from .models import Event
from .forms import EventForm
from .models import User
from .utilities import save_user


def create_event(ev_req):
    if ev_req.method == 'POST':
        form = EventForm(ev_req.POST) 
        if form.is_valid():
            form.save()
            return redirect('event_list')
    else:
        form = EventForm() # creates empty form 

    return render(ev_req, 'create_event.html', {'form': form})


def register_user(request):
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            save_user(form.cleaned_data)
            return redirect('login')
    else:
        form = UserCreationForm()

    return render(request, 'register.html', {'form': form})