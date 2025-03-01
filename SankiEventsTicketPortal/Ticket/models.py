from django.db import models


class AssignedTicket(models.Model):
    event_date_id = models.CharField(max_length=10)
    reseller_id = models.CharField(max_length=10)
    assigned_tickets = models.IntegerField()

    def __str__(self):
        return f"{self.reseller.username} - {self.event_date.date}"


class Ticket(models.Model):
    ticket_id = models.AutoField(primary_key=True)
    event_date_id = models.CharField(max_length=10)
    seller_id = models.CharField(max_length=10)
    
    qty = models.IntegerField()
    amount = models.IntegerField()
    sold_date = models.DateField()
    customer_name = models.CharField(max_length=255)
    customer_email = models.EmailField()
    customer_number = models.CharField(max_length=20)
    customer_payment_ss = models.CharField(max_length=255)
    
    approved = models.BooleanField(default=False)
    mail_sent = models.BooleanField(default=False)
    ticket_sent_codes = models.CharField(max_length=255)

    def __str__(self):
        return f"Ticket {self.ticket_id} - {self.customer_name}"

