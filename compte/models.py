from django.db import models
from django.contrib.auth.models import AbstractUser

# Create your models here.


class AppUser(AbstractUser):
    is_admin = models.BooleanField(default=False)
    is_superadmin = models.BooleanField(default=False)