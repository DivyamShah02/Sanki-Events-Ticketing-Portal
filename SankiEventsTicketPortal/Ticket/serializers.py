from rest_framework import serializers
from .models import *

from UserDetail.models import *
from Event.models import *

class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket        
        fields = '__all__'

class QtyAmountTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket        
        fields = ['qty', 'amount']

class HodTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket        
        fields = '__all__'
    
    def to_representation(self, instance):
        representation = super().to_representation(instance)

        if 'seller_id' in representation:
            user_details = User.objects.filter(user_id=representation['seller_id']).first()
            user_name = user_details.name
            representation['seller_name'] = user_name

        if 'event_date_id' in representation:
            event_date_data = EventDate.objects.filter(event_date_id=representation['event_date_id']).first()
            event_data = Event.objects.filter(event_id=representation['event_id']).first()

            event_name = event_data.event_name
            event_date = event_date_data.date

            representation['event_name'] = event_name
            representation['event_date'] = event_date

        if 'approved' in representation:
            if representation['approved'] == True:
                if event_data.digital_pass == True:
                    if representation['mail_sent'] == True:
                        print('hello')
                        representation['status'] = 'Mail Sent'
                        representation['icon'] = 'success'
                    else:
                        representation['status'] = 'Approved'
                        representation['icon'] = 'warning'
                else:
                    representation['status'] = 'Approved'
                    representation['icon'] = 'success'
            else:
                representation['status'] = 'Unapproved'
                representation['icon'] = 'danger'
                    

        return representation


class AssignedTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedTicket        
        fields = '__all__'

