from django.contrib.auth.models import AbstractUser
from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage
from django.utils import timezone

import random
import string

def generate_user_id(self, role_code):
    while True:
        user_id = ''.join(random.choices(string.digits, k=10))
        user_id = role_code + user_id
        if not User.objects.filter(is_active=True, user_id=user_id).exists():
            return user_id


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
    is_rented = models.BooleanField(default=False)
    rented_event_id = models.CharField(null=True, blank=True, max_length=15)
    profile_picture = models.ImageField(upload_to='profile_picture/', storage=S3Boto3Storage(), null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)
    company_logo = models.ImageField(upload_to='profile_picture/', storage=S3Boto3Storage(), null=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.user_id:
            role_codes = {
                'admin': 'AD',
                'hod': 'HO',
                'reseller': 'RE'
            }

            new_user_id = generate_user_id(role_code=role_codes[self.role])
            self.user_id = new_user_id

        super().save(*args, **kwargs)

