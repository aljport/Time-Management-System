from django.urls import path
from . import views

from users.views import index as user_index

app_name = "core"

urlpatterns = [
    path("", user_index, name="index"),
    path("health/", views.health_check, name="health"),
]
