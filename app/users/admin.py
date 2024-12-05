from django.contrib import admin
from users.models import Profile, Friends


admin.site.register(Friends)
admin.site.register(Profile)