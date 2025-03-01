from rest_framework import serializers
from .models import *


class EventSerializer(serializers.ModelSerializer):
    class Meta:
        model = Event        
        fields = '__all__'


class EventDateSerializer(serializers.ModelSerializer):
    class Meta:
        model = EventDate        
        fields = '__all__'

