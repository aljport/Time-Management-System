from django.contrib.auth.views import LoginView, LogoutView
from django.contrib import admin
from django.urls import path
# from .views import create_event
# from .views import register_user

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('create/', create_event, name='create_event'),
    # path('register/', register_user, name="register"),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
]
