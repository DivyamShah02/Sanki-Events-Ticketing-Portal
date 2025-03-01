from django.contrib.auth.models import AbstractUser
from django.db import models

class User(AbstractUser):
    ROLE_CHOICES = [
        ('admin', 'Admin'),
        ('hod', 'HOD'),
        ('reseller', 'Reseller'),
    ]
    role = models.CharField(max_length=20, choices=ROLE_CHOICES)
    user_id = models.CharField(max_length=12, unique=True)  # Ensure user_id is unique
    name = models.CharField(max_length=255)
    contact_number = models.CharField(max_length=15)
