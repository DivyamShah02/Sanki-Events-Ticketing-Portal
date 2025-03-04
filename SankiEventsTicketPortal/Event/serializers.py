from rest_framework import serializers
from .models import *

from Ticket.models import *
from Ticket.serializers import *


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

class HodDashboardEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], approved=True)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj).data

            total_event_ticket_sold = 0
            total_event_ticket_sold_amount = 0

            for ticket_sold in all_envents_tickets_sold:
                total_event_ticket_sold+=ticket_sold['qty']
                total_event_ticket_sold_amount+=ticket_sold['amount']

            representation['total_event_ticket_sold'] = total_event_ticket_sold
            representation['total_event_ticket_sold_amount'] = total_event_ticket_sold_amount

            event_dates_count = len(EventDate.objects.filter(event_id=representation['event_id']))
            representation['event_dates_count'] = event_dates_count

        return representation


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate        
        fields = '__all__'

