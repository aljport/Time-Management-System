from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path
# from OnSchedule.views import create_event

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    # path('create_event/', create_event, name='create_event'),
]
