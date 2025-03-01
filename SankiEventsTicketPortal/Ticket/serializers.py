from rest_framework import serializers
from .models import *


class TicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ticket        
        fields = '__all__'


class AssignedTicketSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignedTicket        
        fields = '__all__'

