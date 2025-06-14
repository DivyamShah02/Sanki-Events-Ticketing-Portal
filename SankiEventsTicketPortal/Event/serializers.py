from rest_framework import serializers
from .models import *

from Ticket.models import *
from Ticket.serializers import *


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            event_dates = EventDate.objects.filter(event_id=representation['event_id'])
            
            all_dates = []
            for event_date in event_dates:
                all_dates.append(f'{event_date.date.day}/{event_date.date.month}')

            representation['all_dates'] = all_dates

        return representation
class HodDashboardEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], approved=True)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

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

class HodEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], approved=True)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

            total_event_ticket_sold = 0
            total_event_ticket_sold_amount = 0

            for ticket_sold in all_envents_tickets_sold:
                total_event_ticket_sold+=ticket_sold['qty']
                total_event_ticket_sold_amount+=ticket_sold['amount']

            representation['total_event_ticket_sold'] = total_event_ticket_sold
            representation['total_event_ticket_sold_amount'] = total_event_ticket_sold_amount

            event_dates = EventDate.objects.filter(event_id=representation['event_id'])
            event_dates_count = len(EventDate.objects.filter(event_id=representation['event_id']))
            representation['event_dates_count'] = event_dates_count

            final_event_dates_list = []
            number_of_tickets = 0
            total_number_of_tickets = 0
            all_dates = []

            for event_date in event_dates:
                temp_event = {
                    'event_date_id': event_date.event_date_id,
                    'event_date': f'{event_date.date.day}/{event_date.date.month}/{event_date.date.year}',        
                    'number_of_tickets': event_date.number_of_tickets,            
                    'tickets_sold': 0,
                    'tickets_sold_amount': 0
                }
                all_dates.append(f'{event_date.date.day}/{event_date.date.month}')

                number_of_tickets+=int(event_date.number_of_tickets)
                total_number_of_tickets+=int(event_date.total_number_of_tickets)

                all_envents_tickets_sold_obj = Ticket.objects.filter(event_date_id=event_date.event_date_id, approved=True)
                all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

                for ticket_sold in all_envents_tickets_sold:
                    temp_event['tickets_sold']+=ticket_sold['qty']
                    temp_event['tickets_sold_amount']+=ticket_sold['amount']
                
                final_event_dates_list.append(temp_event)

            representation['event_dates_data'] = final_event_dates_list
            representation['number_of_tickets'] = number_of_tickets
            representation['total_number_of_tickets'] = total_number_of_tickets
            representation['all_dates'] = all_dates

        return representation

def repeat_to_length(input_list, target_length):
    if not input_list:
        return []  # or raise an error if empty input is invalid

    repeated_list = (input_list * (target_length // len(input_list) + 1))[:target_length]
    return repeated_list

class HodEventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            event_date_id = self.context.get('event_date_id', None)
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], event_date_id=event_date_id)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data
            all_tickets = HodTicketSerializer(all_envents_tickets_sold_obj, many=True).data
            # all_tickets = repeat_to_length(all_tickets, 103)
            representation['all_tickets'] = all_tickets[::-1]

            total_event_ticket_sold = 0
            total_event_ticket_sold_amount = 0

            for ticket_sold in all_envents_tickets_sold:
                total_event_ticket_sold+=ticket_sold['qty']
                total_event_ticket_sold_amount+=ticket_sold['amount']

            representation['total_event_ticket_sold'] = total_event_ticket_sold
            representation['total_event_ticket_sold_amount'] = total_event_ticket_sold_amount

            event_dates = EventDate.objects.filter(event_id=representation['event_id'])
            event_dates_count = len(EventDate.objects.filter(event_id=representation['event_id']))
            representation['event_dates_count'] = event_dates_count

            final_event_dates_list = []
            number_of_tickets = 0
            all_dates = []

            for event_date in event_dates:
                temp_event = {
                    'event_date_id': event_date.event_date_id,
                    'event_date': f'{event_date.date.day}/{event_date.date.month}/{event_date.date.year}',        
                    'number_of_tickets': event_date.number_of_tickets,            
                    'tickets_sold': 0,
                    'tickets_sold_amount': 0
                }
                all_dates.append(f'{event_date.date.day}/{event_date.date.month}')

                number_of_tickets+=int(event_date.number_of_tickets)

                all_envents_tickets_sold_obj = Ticket.objects.filter(event_date_id=event_date.event_date_id, approved=True)
                all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

                for ticket_sold in all_envents_tickets_sold:
                    temp_event['tickets_sold']+=ticket_sold['qty']
                    temp_event['tickets_sold_amount']+=ticket_sold['amount']
                
                final_event_dates_list.append(temp_event)

            representation['event_dates_data'] = final_event_dates_list
            representation['number_of_tickets'] = number_of_tickets
            representation['all_dates'] = all_dates

        return representation

class ResellerDashboardEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            seller_id = self.context.get('seller_id', None)
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], approved=True, seller_id=seller_id)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

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

class ResellerEventsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            seller_id = self.context.get('seller_id', None)
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], approved=True, seller_id=seller_id)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

            total_event_ticket_sold = 0
            total_event_ticket_sold_amount = 0

            for ticket_sold in all_envents_tickets_sold:
                total_event_ticket_sold+=ticket_sold['qty']
                total_event_ticket_sold_amount+=ticket_sold['amount']

            representation['total_event_ticket_sold'] = total_event_ticket_sold
            representation['total_event_ticket_sold_amount'] = total_event_ticket_sold_amount

            event_dates = EventDate.objects.filter(event_id=representation['event_id'])
            event_dates_count = len(EventDate.objects.filter(event_id=representation['event_id']))
            representation['event_dates_count'] = event_dates_count

            final_event_dates_list = []
            number_of_tickets = 0
            all_dates = []

            for event_date in event_dates:
                temp_event = {
                    'event_date_id': event_date.event_date_id,
                    'event_date': f'{event_date.date.day}/{event_date.date.month}/{event_date.date.year}',        
                    'number_of_tickets': event_date.number_of_tickets,            
                    'tickets_sold': 0,
                    'tickets_sold_amount': 0
                }
                all_dates.append(f'{event_date.date.day}/{event_date.date.month}')
                
                seller_assigned_tickets = AssignedTicket.objects.filter(event_date_id=event_date.event_date_id, reseller_id=seller_id).first()
                number_of_tickets += seller_assigned_tickets.assigned_tickets if seller_assigned_tickets else 0

                all_envents_tickets_sold_obj = Ticket.objects.filter(event_date_id=event_date.event_date_id, approved=True, seller_id=seller_id)
                all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data

                for ticket_sold in all_envents_tickets_sold:
                    temp_event['tickets_sold']+=ticket_sold['qty']
                    temp_event['tickets_sold_amount']+=ticket_sold['amount']
                
                final_event_dates_list.append(temp_event)

            representation['event_dates_data'] = final_event_dates_list
            representation['number_of_tickets'] = number_of_tickets
            representation['all_dates'] = all_dates

        return representation

class ResellerEventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'

    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'event_id' in representation:
            event_date_id = self.context.get('event_date_id', None)
            seller_id = self.context.get('seller_id', None)
            all_envents_tickets_sold_obj = Ticket.objects.filter(event_id=representation['event_id'], event_date_id=event_date_id, seller_id=seller_id)
            all_envents_tickets_sold = QtyAmountTicketSerializer(all_envents_tickets_sold_obj, many=True).data
            all_tickets = ResellerTicketSerializer(all_envents_tickets_sold_obj, many=True).data
            representation['all_tickets'] = all_tickets[::-1]

            total_event_ticket_sold = 0
            total_event_ticket_sold_amount = 0
            total_approved_event_ticket = 0

            for ticket_sold in all_envents_tickets_sold:
                total_event_ticket_sold+=ticket_sold['qty']
                total_event_ticket_sold_amount+=ticket_sold['amount']
                if ticket_sold['approved'] == True:
                    total_approved_event_ticket+=ticket_sold['qty']

            representation['total_event_ticket_sold'] = total_event_ticket_sold
            representation['total_event_ticket_sold_amount'] = total_event_ticket_sold_amount
            representation['total_approved_event_ticket'] = total_approved_event_ticket
            
            all_dates = []
            seller_assigned_tickets = AssignedTicket.objects.filter(event_date_id=event_date_id, reseller_id=seller_id).first()
            representation['assigned_tickets'] = seller_assigned_tickets.assigned_tickets if seller_assigned_tickets else 0

            representation['total_number_of_tickets'] = EventDate.objects.filter(event_date_id=event_date_id).first().total_number_of_tickets
            representation['all_dates'] = all_dates

        return representation

class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate        
        fields = '__all__'

