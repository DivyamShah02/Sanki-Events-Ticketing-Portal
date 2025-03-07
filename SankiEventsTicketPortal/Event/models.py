from django.db import models


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
    # event_images = models.JSONField()
    digital_pass = models.BooleanField(default=False)
    s3_bucket_folder = models.CharField(max_length=255)

    def __str__(self):
        return self.event_name


class EventDate(models.Model):
    event_date_id = models.CharField(max_length=10, unique=True)
    event_id = models.CharField(max_length=10)
    date = models.DateField()
    number_of_tickets = models.IntegerField()

    def __str__(self):
        return f"{self.event_date_id} - {self.date}"

