import csv
import json
import random
import string
import xlsxwriter
import pandas as pd
from io import BytesIO
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import get_object_or_404
from django.utils.timezone import now
from django.http import HttpResponse

from utils.decorators import *
from utils.handle_s3_bucket import *

from .models import *
from .serializers import *
from .generate_pass import generate_pass

from UserDetail.models import *
from Event.models import *
from Event.serializers import *


class TicketViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    def create(self, request):
        required_fields = ['seller_id', 'event_date_id', 'event_id', 'qty', 'amount',
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
            sold_date=datetime.now(),
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

class EventTicketViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    def create(self, request):
        required_fields = ['seller_id', 'event_date', 'event_id', 'qty', 'amount',
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
        
        event_date_obj = EventDate.objects.filter(event_id=request.data.get('event_id'), date=request.data.get('event_date')).first()
        if not event_date_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event date not found."
                }, status=status.HTTP_400_BAD_REQUEST)

        event_date_id = event_date_obj.event_date_id
        
        ticket_id = self.generate_ticket_id()
        
        new_ticket = Ticket.objects.create(
            ticket_id=ticket_id,
            seller_id=request.data.get('seller_id'),
            event_date_id=event_date_id,
            event_id=request.data.get('event_id'),
            qty=int(request.data.get('qty')),
            amount=int(request.data.get('amount')),
            sold_date=datetime.now(),
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
    
    # @handle_exceptions
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

        event_data_obj = Event.objects.filter(event_id=ticket_data.event_id).first()        
        event_date_data_obj = EventDate.objects.filter(event_date_id=ticket_data.event_date_id).first()        

        mail_sent = self.send_mail(event_name=event_data_obj.event_name,
                                    date=event_date_data_obj.date,
                                    recipient_email=ticket_data.customer_email,
                                    qty=ticket_data.qty)

        if mail_sent:
            ticket_data.save()

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {"ticket_id": ticket_id},
                "error": None
            }, status=status.HTTP_200_OK)

    def send_mail(self, event_name, date, recipient_email, qty):
        success = send_approve_mail(
                event_name=event_name,
                # date="2025-05-20 00:00:00",
                date=f"{date} 00:00:00",
                recipient_email=recipient_email,
                qty=qty
            )

        if success:
            print(f"Sent Mail!")
            return True

        else:
            return False


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
        event_date_data_obj = EventDate.objects.filter(event_date_id=ticket_data.event_date_id).first()        

        print(event_data_obj.event_name)
        print(event_date_data_obj.date)
        print(ticket_data.customer_email)
        print(ticket_data.qty)

        if event_data_obj.digital_pass == True:            
            mail_sent, status_text = self.send_mail(event_name=event_data_obj.s3_bucket_folder,
                                                    date=event_date_data_obj.date,
                                                    recipient_email=ticket_data.customer_email,
                                                    qty=ticket_data.qty)

            if mail_sent:
                ticket_data.mail_sent = True
                ticket_data.ticket_sent_codes = status_text
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
                        "error": f'Unable to send mail: {status_text}'
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

    def send_mail(self, event_name, date, recipient_email, qty):
        filename, success, *error = send_ticket_and_move(
                event_name=event_name,
                # date="2025-05-20 00:00:00",
                date=f"{date} 00:00:00",
                recipient_email=recipient_email,
                qty=qty
            )

        if success:
            print(f"Sent and moved file: {filename}")
            return True, filename

        else:
            print("Failed:", error[0])
            return False, error[0]


class ReSendTicketMailViewSet(viewsets.ViewSet):
    
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
        event_date_data_obj = EventDate.objects.filter(event_date_id=ticket_data.event_date_id).first()        

        print(event_data_obj.event_name)
        print(event_date_data_obj.date)
        print(ticket_data.customer_email)
        print(ticket_data.qty)
        print(ticket_data.ticket_sent_codes)
        
        ticket_sent_codes = ticket_data.ticket_sent_codes
        try:
            ticket_sent_codes = json.loads(ticket_sent_codes.replace("'", '"'))
        except:
            ticket_sent_codes = []

        if event_data_obj.digital_pass == True:            
            mail_sent, status_text = self.re_send_mail(event_name=event_data_obj.s3_bucket_folder,
                                                    date=event_date_data_obj.date,
                                                    recipient_email=ticket_data.customer_email,
                                                    qty=ticket_data.qty,sent_files=ticket_sent_codes)

            if mail_sent:
                ticket_data.mail_sent = True
                ticket_data.ticket_sent_codes = status_text
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
                        "error": f'Unable to send mail: {status_text}'
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

    def re_send_mail(self, event_name, date, recipient_email, qty, sent_files):
        filename, success, *error = resend_ticket(
                event_name=event_name,
                # date="2025-05-20 00:00:00",
                date=f"{date} 00:00:00",
                recipient_email=recipient_email,
                qty=qty,
                sent_files=sent_files
            )
        if len(sent_files) == 0:
            print("No files to resend.")
            return False, "No files to resend."

        if success:
            print(f"ReSent file: {filename}")
            return True, filename

        else:
            print("Failed:", error[0])
            return False, error[0]


class AssignTicketViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication('hod')
    def create(self, request):
        reseller_id = request.data.get('reseller_id')
        event_date_id = request.data.get('event_date_id')
        assigned_tickets = request.data.get('assigned_tickets')
        ticket_price = request.data.get('ticket_price')

        if (not reseller_id) or (not event_date_id) or (not assigned_tickets):
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"All details are required."
                }, status=status.HTTP_400_BAD_REQUEST)

        ticket_already_assigned = AssignedTicket.objects.filter(reseller_id=reseller_id, event_date_id=event_date_id).first()
        if not ticket_already_assigned:
            assign_ticket = AssignedTicket.objects.create(
                reseller_id=reseller_id,
                event_date_id=event_date_id,
                assigned_tickets=assigned_tickets,
            )
            assign_ticket.save()
        else:
            ticket_already_assigned.assigned_tickets = int(ticket_already_assigned.assigned_tickets) + int(assigned_tickets)
            ticket_already_assigned.save()

        event_date_obj = EventDate.objects.filter(event_date_id=event_date_id).first()        
        
        extra_assigned_tickets = int(assigned_tickets) - (int(event_date_obj.total_number_of_tickets) - int(event_date_obj.number_of_tickets))
        if extra_assigned_tickets < 0:
            extra_assigned_tickets = 0
        event_date_obj.total_number_of_tickets = int(event_date_obj.total_number_of_tickets) + extra_assigned_tickets

        event_date_obj.number_of_tickets = int(event_date_obj.number_of_tickets) + int(assigned_tickets)
        event_date_obj.save()

        assigned_ticket_history = AssignedTicketHistory.objects.create(
            ticket_qty=assigned_tickets,
            ticket_price=ticket_price,
            reseller_id=reseller_id,
            event_date_id=event_date_id
        )
        assigned_ticket_history.save()

        return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {'assigned_tickets': assigned_tickets},
                "error": None
            }, status=status.HTTP_200_OK)


class AdminExportAssignedTicketDataViewSet(viewsets.ViewSet):

    # @handle_exceptions
    @check_authentication('hod')
    def list(self, request, pk='csv'):
        """
        Export orders to CSV or Excel
        """
        event_date_id = request.GET.get('event_date_id')
        if not event_date_id:
            return Response({"success": False, "error": "event_date_id is required"}, status=400)

        assigned_tickets_obj = AssignedTicketHistory.objects.filter(event_date_id=event_date_id)
        assigned_tickets_data = AssignedTicketHistorySerializer(assigned_tickets_obj, many=True).data
        if not assigned_tickets_data:
            return Response({"success": False, "error": "No tickets found for the given event date"}, status=404)

        file_name = f"{assigned_tickets_data[0]['event_name']} - {assigned_tickets_data[0]['event_date']} Tickets assigned" if assigned_tickets_data else 'Event_data'
        if pk == 'csv':
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = f'attachment; filename="{file_name}.csv"'
            
            writer = csv.writer(response)
            writer.writerow([
                'Date', 'Event Name', 'Event Date', 'Reseller Name', 'Ticket Quantity', 'Total Ticket Price'
            ])
            
            for assigned_ticket in assigned_tickets_data:
                writer.writerow([
                    assigned_ticket['created_at'],
                    assigned_ticket['event_name'],
                    assigned_ticket['event_date'],
                    assigned_ticket['reseller_name'],
                    assigned_ticket['ticket_qty'],
                    assigned_ticket['ticket_price'],
                ])
            
            return response
        
        elif pk == 'excel':
            output = BytesIO()
            workbook = xlsxwriter.Workbook(output)
            worksheet = workbook.add_worksheet()
            
            # Add header row
            headers = [
                'Date', 'Event Name', 'Event Date', 'Reseller Name', 'Ticket Quantity', 'Total Ticket Price'
            ]
            
            for col, header in enumerate(headers):
                worksheet.write(0, col, header)
            
            # Add data rows
            for row, assigned_ticket in enumerate(assigned_tickets_data, start=1):
                worksheet.write(row, 0, assigned_ticket['created_at'])
                worksheet.write(row, 1, assigned_ticket['event_name'])
                worksheet.write(row, 2, assigned_ticket['event_date'])
                worksheet.write(row, 3, assigned_ticket['reseller_name'])
                worksheet.write(row, 4, assigned_ticket['ticket_qty'])
                worksheet.write(row, 5, assigned_ticket['ticket_price'])                
            
            workbook.close()
            output.seek(0)
            
            response = HttpResponse(
                output.read(),
                content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
            )
            response['Content-Disposition'] = f'attachment; filename="{file_name}.xlsx"'
            return response
        
        elif pk == 'pdf':
            # PDF export would require a PDF library like ReportLab
            # This is a placeholder for future implementation
            return Response({"success": False, "error": "PDF export not implemented yet"}, status=501)
        
        else:
            return Response({"success": False, "error": f"Invalid export format: {pk}"}, status=400)


class AddAvailableTicketsViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication('hod')
    def create(self, request):        
        event_date_id = request.data.get('event_date_id')
        new_available_tickets = request.data.get('new_available_tickets')

        if (not event_date_id) or (not new_available_tickets):
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"All details are required."
                }, status=status.HTTP_400_BAD_REQUEST)

        event_date_obj = EventDate.objects.filter(event_date_id=event_date_id).first()        

        event_date_obj.total_number_of_tickets = int(event_date_obj.total_number_of_tickets) + int(new_available_tickets)
        event_date_obj.save()

        return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": {'new_available_tickets': new_available_tickets},
                "error": None
            }, status=status.HTTP_200_OK)


class TicketPassViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        ticket_id = request.GET.get('ticket_id')

        if not ticket_id:
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"All details are required."
                }, status=status.HTTP_400_BAD_REQUEST)

        ticket_data = Ticket.objects.filter(ticket_id=ticket_id).first()
        if not ticket_data:
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": f"Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_data = Event.objects.filter(event_id=ticket_data.event_id).first()
        pass_qr_dimension = str(event_data.pass_qr_dimension)
        pass_path = event_data.event_pass.url

        qr_size = tuple(map(int, pass_qr_dimension.split('|')[0].strip().split(',')))
        qr_position = tuple(map(int, pass_qr_dimension.split('|')[1].strip().split(',')))
        text_position = tuple(map(int, pass_qr_dimension.split('|')[2].strip().split(',')))

        buffer = generate_pass(ticket_id=ticket_id, name=ticket_data.customer_name, qr_size=qr_size, qr_position=qr_position, text_position=text_position, pass_path=pass_path)
        
        response = HttpResponse(buffer, content_type="image/png")
        response["Content-Disposition"] = 'attachment; filename="Event_Pass.png"'

        return response


class ValidateTicketPassViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        ticket_id = request.GET.get('ticket_id')

        if not ticket_id:
            data = {
                "isValid": False,
                "customerName": ''
            }
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": data,
                    "error": f"All details are required."
                }, status=status.HTTP_400_BAD_REQUEST)

        ticket_data = Ticket.objects.get(ticket_id=ticket_id)
        if not ticket_data:
            data = {
                "isValid": False,
                "customerName": ''
            }
            return Response({
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": data,
                    "error": f"Ticket not found."
                }, status=status.HTTP_404_NOT_FOUND)

        if ticket_data.scanned:
            data = {
                "isValid": False,
                "already_scanned": True,
                "customerName": ticket_data.customer_name
            }
        else:
            ticket_data.scanned = True
            ticket_data.save()
            data = {
                    "isValid": True,
                    "already_scanned": False,
                    "customerName": ticket_data.customer_name
                }
        return Response({
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class TicketExportViewSet(viewsets.ViewSet):

    
    def list(self, request):
        # Get filters
        seller_id = request.query_params.get('seller_id')      # Optional
        event_id = request.query_params.get('event_id')        # Optional
        event_date = request.query_params.get('event_date')  # Optional
        created_from = request.query_params.get('created_from')    # Optional
        created_to = request.query_params.get('created_to')        # Optional

        # Initial queryset
        tickets = Ticket.objects.all()

        # Apply time filter (always included)
        if created_from:
            tickets = tickets.filter(created_at__gte=created_from)
        if created_to:
            tickets = tickets.filter(created_at__lte=created_to)

        # Apply other filters if present
        if event_id:
            tickets = tickets.filter(event_id=event_id)
        if event_date:
            event_date_data = EventDate.objects.filter(event_id=event_id, date=event_date).first()
            if event_date_data:
                event_date_id = event_date_data.event_date_id
                tickets = tickets.filter(event_date_id=event_date_id)

        # CASE A: Single seller
        if seller_id:
            tt_seller_name = User.objects.filter(user_id=seller_id).first()
            seller_tickets = tickets.filter(seller_id=seller_id)
            df = self.serialize_tickets(seller_tickets)
            return self.export_excel(df, f"{tt_seller_name.name}_Tickets")

        # CASE B: All or multiple sellers – multi-sheet export
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            sellers = tickets.values_list('seller_id', flat=True).distinct()
            for sid in sellers:
                seller_tickets = tickets.filter(seller_id=sid)
                if seller_tickets.exists():
                    seller_name = User.objects.filter(user_id=sid).first()
                    sheet_name = (seller_name.name if seller_name else sid)[:31]
                    df = self.serialize_tickets(seller_tickets)
                    df.to_excel(writer, sheet_name=sheet_name, index=False)

        buffer.seek(0)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"Tickets_Export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response


    def serialize_tickets(self, queryset):
        data = []

        # Cache event and event date info
        event_map = {e.event_id: e for e in Event.objects.all()}
        event_date_map = {ed.event_date_id: ed for ed in EventDate.objects.all()}

        # Group EventDate by event_id to compute positions
        event_date_positions = {}
        for ed in EventDate.objects.all():
            event_date_positions.setdefault(ed.event_id, []).append(ed.date)

        # Sort all date lists
        for k in event_date_positions:
            event_date_positions[k].sort()

        for t in queryset:
            event = event_map.get(t.event_id)
            ed = event_date_map.get(t.event_date_id)

            event_name = event.event_name if event else ''
            event_date = ed.date if ed else None

            day_of_event = ''
            weekday_name = ''

            if event_date and event:
                sorted_dates = event_date_positions.get(t.event_id, [])
                try:
                    day_index = sorted_dates.index(event_date)
                    day_of_event = f"{day_index + 1} Day"
                    weekday_name = event_date.strftime('%A')
                except ValueError:
                    day_of_event = 'N/A'
                    weekday_name = 'N/A'
            status_ticket = 'Unapproved'
            if t.approved:
                status_ticket = 'Approved'
            if t.mail_sent:
                status_ticket = 'Mail Sent'
            data.append({
                "Event Name": event_name,
                "Event ID": t.event_id,
                "Ticket ID": t.ticket_id,
                "Event Date ID": t.event_date_id,
                "Event Date": event_date.strftime('%Y-%m-%d') if event_date else '',
                "Day of Event": day_of_event,
                "Weekday": weekday_name,
                "Seller ID": t.seller_id,
                "Qty": t.qty,
                "Amount": t.amount,
                "Sold Date": t.sold_date.strftime('%Y-%m-%d'),
                "Customer Name": t.customer_name,
                "Customer Email": t.customer_email,
                "Customer Number": t.customer_number,
                "Status": status_ticket,
                "Created At": t.created_at.strftime('%Y-%m-%d %H:%M:%S'),
            })

        return pd.DataFrame(data)

    def export_excel(self, df, sheet_name):
        buffer = BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name=sheet_name[:31], index=False)
        buffer.seek(0)
        response = HttpResponse(
            buffer.read(),
            content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
        )
        filename = f"{sheet_name}_Export_{timezone.now().strftime('%Y%m%d_%H%M%S')}.xlsx"
        response['Content-Disposition'] = f'attachment; filename={filename}'
        return response
