from django.urls import path
from django.contrib import admin
from . import views

app_name = "users"

urlpatterns = [
    path("", views.index, name="user_landing"),
    path('login/', views.login_page, name = 'login_page'),
    path('register/', views.register_page, name = 'register_page'),
    path('username_get/', views.username_get_page, name = 'username_get_page'),
    path('password_reset/', views.password_reset_page, name = "password_reset"),
    path('password_change/', views.password_change_page, name = 'password_change_page'),
    path('password_confirm/', views.password_confirm_page, name = 'password_confirm_page'),
    path('account_information/', views.account_information_page, name = 'account_information_page'),
    path('friend_list/', views.friend_list_page, name = 'friend_list_page'),
    path('update-friend-list/<int:friend_id>/', views.update_friendList, name='update_friendList'),
]