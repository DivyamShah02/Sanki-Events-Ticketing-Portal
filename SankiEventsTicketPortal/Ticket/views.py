import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils.timezone import now

from utils.decorators import *

from .models import *
from .serializers import *

from UserDetail.models import *
from Event.models import *
from Event.serializers import *


class TicketViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    def create(self, request):
        required_fields = ['seller_id', 'event_date_id', 'event_id', 'qty', 'amount', 'sold_date',
                           'customer_name', 'customer_email', 'customer_number']
        for field in required_fields:
            if field not in request.data:
                return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"{field} is required."
                }, status=status.HTTP_400_BAD_REQUEST)

        seller_data = User.objects.filter(user_id=request.data['seller_id']).first()
        if not seller_data:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Seller not found."
                }, status=status.HTTP_400_BAD_REQUEST)

        ticket_id = self.generate_ticket_id()
        new_ticket = Ticket.objects.create(
            ticket_id=ticket_id,
            seller_id=request.data.get('seller_id'),
            event_date_id=request.data.get('event_date_id'),
            event_id=request.data.get('event_id'),
            qty=int(request.data.get('qty')),
            amount=int(request.data.get('amount')),
            sold_date=request.data.get('sold_date'),
            customer_name=request.data.get('customer_name'),
            customer_email=request.data.get('customer_email'),
            customer_number=request.data.get('customer_number'),
            customer_payment_ss=request.FILES.get('customer_payment_ss', None),
            approved=False,
            mail_sent=False,
            ticket_sent_codes=""
        )

        return Response({
            "success": True,
            "user_not_logged_in": False,
            "user_unauthorized": False,
            "data": {'ticket_id': ticket_id},
            "error": None
        }, status=status.HTTP_201_CREATED)

    def generate_ticket_id(self):
        while True:
            ticket_id = ''.join(random.choices(string.digits, k=10))
            if not Ticket.objects.filter(ticket_id=ticket_id).exists():
                return ticket_id

    @handle_exceptions
    @check_authentication()
    def list(self, request):
        ticket_id = request.data.get('ticket_id')
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "ticket_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        ticket_data_obj = Ticket.objects.filter(ticket_id=ticket_id).first()
        if not ticket_data_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        ticket_data = TicketSerializer(ticket_data_obj).data
        data = {
            'ticket_data': ticket_data
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
    @check_authentication()
    def update(self, request):
        ticket_id = request.data.get('ticket_id')
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "ticket_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        ticket_data = Ticket.objects.get(ticket_id=ticket_id)
        if not ticket_data:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        ticket_data.qty=int(request.data.get('qty', ticket_data.qty))
        ticket_data.amount=int(request.data.get('amount', ticket_data.amount))
        ticket_data.customer_name=request.data.get('customer_name', ticket_data.customer_name)
        ticket_data.customer_email=request.data.get('customer_email', ticket_data.customer_email)
        ticket_data.customer_number=request.data.get('customer_number', ticket_data.customer_number)

        ticket_data.save()
        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"ticket_id": ticket_id},
                "error": None
            }, status=status.HTTP_200_OK)


class AllTicketViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication()
    def list(self, request):
        seller_id = request.GET.get('seller_id')
        event_date_id = request.GET.get('event_date_id')
        event_id = request.GET.get('event_id')
        if seller_id and event_date_id:
            all_tickets_obj = Ticket.objects.filter(event_date_id=event_date_id, seller_id=seller_id)

        elif seller_id:
            all_tickets_obj = Ticket.objects.filter(seller_id=seller_id)

        elif event_date_id:
            all_tickets_obj = Ticket.objects.filter(event_date_id=event_date_id)

        elif event_id:            
            all_tickets_obj = Ticket.objects.filter(event_id=event_id)

        else:
            all_tickets_obj = Ticket.objects.all()

        all_event = EventDateSerializer(all_tickets_obj, many=True).data

        data = {
            'all_event': all_event,
            'len_all_event': len(all_event)
        }

        return Response({
            "success": True,
            "user_not_logged_in": False,
            "user_unauthorized": False,
            "data": data,
            "error": None
        }, status=status.HTTP_201_CREATED)


class ApproveTicketViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    @check_authentication()
    def create(self, request):
        ticket_id = request.data.get('ticket_id')
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "ticket_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        ticket_data = Ticket.objects.get(ticket_id=ticket_id)
        if not ticket_data:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        ticket_data.qty=int(request.data.get('qty', ticket_data.qty))
        ticket_data.amount=int(request.data.get('amount', ticket_data.amount))
        ticket_data.approved = True

        ticket_data.save()

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"ticket_id": ticket_id},
                "error": None
            }, status=status.HTTP_200_OK)


class SendTicketMailViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    @check_authentication()
    def create(self, request):
        ticket_id = request.data.get('ticket_id')
        if not ticket_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "ticket_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)
        
        ticket_data = Ticket.objects.get(ticket_id=ticket_id)
        if not ticket_data:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        event_data_obj = Event.objects.filter(event_id=ticket_data.event_id).first()
        event_data = EventSerializer(event_data).data

        event_date_data_obj = EventDate.objects.filter(event_date_id=ticket_data.event_date_id).first()
        event_date_data = EventDateSerializer(event_date_data_obj).data

        if event_data_obj.digital_pass == True:
            mail_sent = self.send_mail()

            if mail_sent:
                ticket_data.mail_sent = True
                ticket_data.save()

                return Response(
                    {
                        "success": True,
                        "user_not_logged_in": False,
                        "user_unauthorized": False,
                        "data": {"ticket_id": ticket_id},
                        "error": None
                    }, status=status.HTTP_200_OK)

            else:
                return Response(
                    {
                        "success": False,
                        "user_not_logged_in": False,
                        "user_unauthorized": False,
                        "data": None,
                        "error": 'Unable to send mail.'
                    }, status=status.HTTP_400_BAD_REQUEST)

        else:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": 'Event does not has digital pass.'
                }, status=status.HTTP_400_BAD_REQUEST)

    def send_mail(self):
        return True


class AssignTicketViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication()
    def create(self, request):
        reseller_id = request.data.get('reseller_id')
        event_date_id = request.data.get('event_date_id')
        assigned_tickets = request.data.get('assigned_tickets')

        if (not reseller_id) or (not event_date_id) or (not assigned_tickets):
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"All details are required."
                }, status=status.HTTP_400_BAD_REQUEST)

        ticket_already_assigned = AssignedTicket.objects.filter(reseller_id=reseller_id, event_date_id=event_date_id).first()
        if ticket_already_assigned:
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"Ticket already assigned."
                }, status=status.HTTP_400_BAD_REQUEST)

        assign_ticket = AssignedTicket.objects.create(
            reseller_id=reseller_id,
            event_date_id=event_date_id,
            assigned_tickets=assigned_tickets,
        )

        return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {'assigned_tickets': assigned_tickets},
                "error": None
            }, status=status.HTTP_200_OK)

    @handle_exceptions
    @check_authentication()
    def list(self, request):
        reseller_id = request.data.get('reseller_id')
        event_date_id = request.data.get('event_date_id')  

        if not event_date_id:
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"event_date_id required."
                }, status=status.HTTP_400_BAD_REQUEST)

        if reseller_id:
            assigned_tickets_obj = AssignedTicket.objects.filter(reseller_id=reseller_id, event_date_id=event_date_id).first()
        
        else:
            assigned_tickets_obj = AssignedTicket.objects.filter(event_date_id=event_date_id)

        assigned_tickets = AssignedTicketSerializer(assigned_tickets_obj, many=True).data

        data = {
            'assigned_tickets': assigned_tickets,
            'len_assigned_tickets': len(assigned_tickets)
        }

        return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)

    @handle_exceptions
    @check_authentication()
    def update(self, request):
        assigned_ticket_id = request.data.get('assigned_ticket_id')
        if not assigned_ticket_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "assigned_ticket_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        assign_ticket_data = AssignedTicket.objects.get(id=assigned_ticket_id)
        if not assign_ticket_data:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Assigned Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        assigned_tickets = int(request.data.get('assigned_tickets', assign_ticket_data.assigned_tickets))
        assign_ticket_data.assigned_tickets = assigned_tickets
        assign_ticket_data.save()

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"assigned_tickets": assigned_tickets},
                "error": None
            }, status=status.HTTP_200_OK)

