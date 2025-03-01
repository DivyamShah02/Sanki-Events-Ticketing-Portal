import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from utils.decorators import *

from .models import *
from .serializers import *
from utils.handle_s3_bucket import create_event_folders_s3


class EventViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication(required_role='hod')
    def create(self, request):
        event_name = request.data.get('event_name')
        event_details = request.data.get('event_details')
        event_venue = request.data.get('event_venue')
        event_date_range = request.data.get('event_date_range')
        digital_pass = request.data.get('digital_pass', False)
        
        if not (event_name and event_details and event_venue and event_date_range):
            return Response(
            {
                "success": False,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": "Missing required fields."
            }, status=status.HTTP_201_CREATED)
        
        event_id = self.generate_event_id()
        hod_id = request.user.user_id
        event_dates = []

        start_date, end_date = event_date_range.split(" | ")
        start_date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        current_date = start_date
        while current_date <= end_date:
            EventDate.objects.create(
                event_id=event_id,
                event_date_id=self.generate_event_date_id(),
                date=current_date.date(),
                number_of_tickets=0
            )
            current_date += timedelta(days=1)
            event_dates.append(current_date)

        s3_bucket_folder = create_event_folders_s3(event_name=event_name, event_dates=event_dates)
        event = Event.objects.create(
            event_id=event_id,
            hod_id=hod_id,
            event_name=event_name,
            event_details=event_details,
            event_venue=event_venue,
            event_date_range=event_date_range,
            digital_pass=digital_pass,
            s3_bucket_folder=s3_bucket_folder
        )

        
        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"event_id": event_id},
                "error": None
            }, status=status.HTTP_201_CREATED)

    def generate_event_id(self):
        while True:
            event_id = ''.join(random.choices(string.digits, k=10))
            if not Event.objects.filter(event_id=event_id).exists():
                return event_id

    def generate_event_date_id(self):
        while True:
            event_date_id = ''.join(random.choices(string.digits, k=10))
            if not EventDate.objects.filter(event_date_id=event_date_id).exists():
                return event_date_id

    @check_authentication()
    @handle_exceptions
    def list(self, request):
        event_id = request.GET.get('event_id')
        if not event_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_obj = Event.objects.filter(event_id=event_id).first()
        if not event_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_data = EventSerializer(event_obj).data

        event_dates_onj = EventDate.objects.filter(event_id=event_id)
        event_dates_data = EventDateSerializer(event_dates_onj, many=True).data

        data = {
            "event_data": event_data,
            "event_dates_data": event_dates_data,
            "len_event_dates_data": event_dates_data
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)

    @handle_exceptions
    @check_authentication(required_role='hod')
    def update(self, request):
        event_id = request.data.get('event_id')
        if not event:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event = Event.objects.filter(event_id=event_id).first()
        if not event:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event.event_name = request.data.get('event_name', event.event_name)
        event.event_details = request.data.get('event_details', event.event_details)
        event.event_venue = request.data.get('event_venue', event.event_venue)

        event.save()
        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"event_id": event_id},
                "error": None
            }, status=status.HTTP_200_OK)

    @handle_exceptions
    @check_authentication(required_role='hod')
    def delete(self, request):
        event_id = request.data.get('event_id')
        if not event:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event = Event.objects.filter(event_id=event_id).first()
        if not event:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        EventDate.objects.filter(event_id=event_id).delete()
        event.delete()

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": None
            }, status=status.HTTP_200_OK)


class EventListViewSet(viewsets.ViewSet):
    @check_authentication()
    @handle_exceptions
    def list(self, request):
        events_obj = Event.objects.all()
        events_data = EventSerializer(events_obj).data
        
        data = {
            'events_data': events_data,
            'len_events_data': len(events_data)
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class EventDetailViewSet(viewsets.ViewSet):
    @check_authentication()
    @handle_exceptions
    def list(self, request):
        event_id = request.GET.get('event_id')
        if not event_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_obj = Event.objects.filter(event_id=event_id).first()
        if not event_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_data = EventSerializer(event_obj).data

        event_dates_onj = EventDate.objects.filter(event_id=event_id)
        event_dates_data = EventDateSerializer(event_dates_onj, many=True).data

        data = {
            "event_data": event_data,
            "event_dates_data": event_dates_data,
            "len_event_dates_data": event_dates_data
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class TicketUpdateViewSet(viewsets.ViewSet):
    @check_authentication(required_role='hod')
    @handle_exceptions
    def create(self, request):
        event_date_id = request.data.get('event_date_id')    
        if not event_date_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_date_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        ticket_count = request.data.get('ticket_count')
        if not ticket_count:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "ticket_count not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_date = EventDate.objects.filter(event_date_id=event_date_id).first()
        if not event_date:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event date not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_date.number_of_tickets = ticket_count
        event_date.save()
        
        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"event_date_id": event_date_id, "ticket_count": ticket_count},
                "error": None
            }, status=status.HTTP_200_OK)

