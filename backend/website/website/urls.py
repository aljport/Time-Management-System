"""
URL configuration for website project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib.auth import views as auth_views
from django.contrib import admin
from django.urls import path, include
from authentication.views import *

urlpatterns = [
    path('home/', home, name = "recipes"), #not needed will replace with calendar page
    path('admin/', admin.site.urls),
    path('login/', login_page, name = 'login_page'),
    path('register/', register_page, name = 'register_page'),
    path('username_get/', username_get_page, name = 'username_get_page'),
    path('password_reset/', password_reset_page, name = "password_reset"),
    path('password_change/', password_change_page, name = 'password_change_page'),
    path('password_confirm/', password_confirm_page, name = 'password_confirm_page'),
    path('account_information/', account_information_page, name = 'account_information_page'),
    path('friend_list/', friend_list_page, name = 'friend_list_page'),
]
