from django.contrib import admin
from .models import Event, Notifications, UnavailableSlot

admin.site.register(Event)
admin.site.register(Notifications)
admin.site.register(UnavailableSlot)