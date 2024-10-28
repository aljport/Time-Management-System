from django.urls import path

from . import views

#pip install django-mathfilters

appName = "cal"

urlpatterns = [
    path("", views.index, name="index"),
    path("week", views.weekview, name="weekview"),
    path("month", views.monthview, name="monthview"),
    path("month/<int:month_date>/<int:day_date>/<int:year_date>", views.monthviewer, name="monthviewer"),
    path("week/<int:month_date>/<int:day_date>/<int:year_date>", views.weekview, name="weekviewer"),
    path("month/<int:month_date>/<int:day_date>/<int:year_date>/<int:selected_day>", views.monthevent, name="monthevent"),

    
]