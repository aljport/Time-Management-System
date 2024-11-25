from django.contrib.auth.models import User
from .models import Event, UnavailableSlot

# is this necessary anymore?
def save_user(user_data):
    username = user_data.get('username')
    email = user_data.get('email')
    password = user_data.get('password')

    user = User.objects.create_user(username=username, email=email, password=password)
    user.save()

def isTimeAvailable(user, start_time, end_time):
    # check for one-time conflicting slots
    conflicting_slot = UnavailableSlot.objects.filter(
        user=user,
        start_time__lt=end_time,
        end_time__gt=start_time
    ).exists()

    # recurring daily conflicts
    daily_conflict = UnavailableSlot.objects.filter(
        user=user,
        recurrence='Daily'
    ).filter(
        start_time__time__lte=start_time.time(),
        end_time__time__gte=end_time.time()
    ).exists()

    # matches both time of day and day of the week
    weekly_conflict = UnavailableSlot.objects.filter(
        user=user,
        recurrence='Weekly'
    ).filter(
        start_time__time__lte=start_time.time(),
        end_time__time__gte=end_time.time(),
        start_time__week_day=start_time.weekday() + 1
    ).exists()

    # handling events that cross midnight (multi-day events)
    cross_day_conflict = UnavailableSlot.objects.filter(
        user=user,
        recurrence__in=['Daily', 'Weekly']
    ).filter(
        start_time__time__gt=end_time.time(),
        end_time__time__lt=start_time.time()
    ).exists()

    # end time exactly matches start of an unavailable slot or vice versa
    edge_case_conflict = UnavailableSlot.objects.filter(
        user=user
    ).filter(
        start_time=end_time  
    ).exists() or UnavailableSlot.objects.filter(
        user=user
    ).filter(
        end_time=start_time
    ).exists()

    # final validation
    return not (conflicting_slot or daily_conflict or weekly_conflict or cross_day_conflict or edge_case_conflict)

