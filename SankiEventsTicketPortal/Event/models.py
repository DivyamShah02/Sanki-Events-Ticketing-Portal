from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class Event(models.Model):
    event_id = models.CharField(max_length=10, unique=True)
    hod_id = models.CharField(max_length=12)
    event_name = models.CharField(max_length=255)
    event_details = models.TextField()
    event_venue = models.CharField(max_length=255)
    event_date_range = models.CharField(max_length=255)
    event_address = models.TextField()
    city = models.CharField(max_length=255)
    state = models.CharField(max_length=255)

    digital_pass = models.BooleanField(default=False)
    s3_bucket_folder = models.CharField(max_length=255)
    event_banner = models.ImageField(upload_to='event_banners/', storage=S3Boto3Storage(), null=True, blank=True)
    event_pass = models.ImageField(upload_to='event_banners/', storage=S3Boto3Storage(), null=True, blank=True)
    pass_qr_dimension = models.CharField(max_length=255, null=True, blank=True)

    is_rented_event = models.BooleanField(default=False)
    is_payment_ss_needed = models.BooleanField(default=False)
    is_qty_predetermined = models.BooleanField(default=False)
    predetermined_qty = models.IntegerField(null=True, blank=True)
    is_free_event = models.BooleanField(default=False)

    def __str__(self):
        return self.event_name


class EventDate(models.Model):
    event_date_id = models.CharField(max_length=10, unique=True)
    event_id = models.CharField(max_length=10)
    date = models.DateField()
    number_of_tickets = models.IntegerField(null=True, blank=True)
    total_number_of_tickets = models.IntegerField(default=0)

    def __str__(self):
        return f"{self.event_date_id} - {self.date}"

