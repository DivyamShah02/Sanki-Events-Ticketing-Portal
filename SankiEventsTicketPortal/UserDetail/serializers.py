from rest_framework import serializers
from .models import *

from Ticket.models import *
from Ticket.serializers import *

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        # fields = ["id", "is_superuser", "username", "first_name", "last_name", "email", "is_staff", "is_active", "date_joined", "role", "user_id", "name", "contact_number", "city", "state"]
        fields = '__all__'


class HodDashboardUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User       
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'user_id' in representation:
            all_tickets_sold_seller_obj = Ticket.objects.filter(seller_id=representation['user_id'], approved=True)
            all_tickets_sold_seller = QtyAmountTicketSerializer(all_tickets_sold_seller_obj, many=True).data

            total_tickets_sold_seller = 0
            total_tickets_sold_seller_amount = 0

            for ticket_sold in all_tickets_sold_seller:
                total_tickets_sold_seller+=ticket_sold['qty']
                total_tickets_sold_seller_amount+=ticket_sold['amount']

            representation['total_tickets_sold_seller'] = total_tickets_sold_seller
            representation['total_tickets_sold_seller_amount'] = total_tickets_sold_seller_amount

        return representation


class HodEventDateDetailUserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User       
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'user_id' in representation:
            event_date_id = self.context.get('event_date_id', None)
            all_tickets_sold_seller_obj = Ticket.objects.filter(seller_id=representation['user_id'], event_date_id=event_date_id)
            all_tickets_sold_seller = QtyAmountTicketSerializer(all_tickets_sold_seller_obj, many=True).data

            total_tickets_sold_seller = 0
            total_tickets_sold_seller_amount = 0

            for ticket_sold in all_tickets_sold_seller:
                total_tickets_sold_seller+=ticket_sold['qty']
                total_tickets_sold_seller_amount+=ticket_sold['amount']

            representation['total_tickets_sold_seller'] = total_tickets_sold_seller
            representation['total_tickets_sold_seller_amount'] = total_tickets_sold_seller_amount

        return representation


