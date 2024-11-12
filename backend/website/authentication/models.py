from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class Friends(models.Model):
    Amigo = models.ForeignKey(User, on_delete=models.CASCADE)
    sharesCalendar = models.BooleanField(default = False)