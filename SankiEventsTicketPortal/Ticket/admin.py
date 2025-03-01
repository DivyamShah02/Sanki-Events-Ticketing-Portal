from django.contrib import admin
from .models import *

@admin.register(Ticket)
class TicketAdmin(admin.ModelAdmin):
    list_display = ('customer_name', 'qty', 'amount', 'sold_date', 'approved', 'mail_sent')
    search_fields = ('customer_name', 'customer_email', 'customer_number', 'id')


@admin.register(AssignedTicket)
class AssignedTicketAdmin(admin.ModelAdmin):
    list_display = ('event_date_id', 'reseller_id', 'assigned_tickets')
    search_fields = ('event_date_id', 'id')

