from django.db import models
from storages.backends.s3boto3 import S3Boto3Storage


class AssignedTicket(models.Model):
    event_date_id = models.CharField(max_length=10)
    reseller_id = models.CharField(max_length=12)
    assigned_tickets = models.IntegerField()

class Ticket(models.Model):
    ticket_id = models.CharField(max_length=10, unique=True)
    event_id = models.CharField(max_length=10)
    event_date_id = models.CharField(max_length=10)
    seller_id = models.CharField(max_length=12)
    
    qty = models.IntegerField()
    amount = models.IntegerField()
    sold_date = models.DateField()
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_number = models.CharField(max_length=20)
    customer_payment_ss = models.ImageField(upload_to='screen_shots/', storage=S3Boto3Storage(), null=True, blank=True)
    
    scanned = models.BooleanField(default=False)
    
    approved = models.BooleanField(default=False)
    mail_sent = models.BooleanField(default=False)
    ticket_sent_codes = models.CharField(max_length=255, default='')

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.customer_name}"

