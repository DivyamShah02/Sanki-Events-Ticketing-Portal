from django.contrib import admin
from .models import *

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ('event_name', 'event_id', 'hod_id', 'digital_pass', 'id')
    search_fields = ('event_name', 'event_id', 'hod_id', 'id')


@admin.register(EventDate)
class EventDateAdmin(admin.ModelAdmin):
    list_display = ('event_id', 'event_date_id', 'date', 'number_of_tickets')
    search_fields = ('event_id', 'event_date_id', 'date', 'id')

