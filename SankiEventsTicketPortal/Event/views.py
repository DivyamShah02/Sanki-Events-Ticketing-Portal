import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from utils.decorators import *

from .models import *
from .serializers import *
from utils.handle_s3_bucket import *
from UserDetail.models import *
from UserDetail.serializers import *


class EventViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication(required_role='hod')
    def create(self, request):
        event_name = request.data.get('event_name')
        event_details = request.data.get('event_details')
        event_venue = request.data.get('event_venue')
        event_date_range = request.data.get('event_date_range')
        event_address = request.data.get('event_address')
        max_pass = request.data.get('max_pass')
        city = request.data.get('city')
        state = request.data.get('state')
        digital_pass = request.data.get('digital_pass', False)
        rented_event = request.data.get('rented_event', False)
        event_banner = request.FILES.get('event_banner', None)

        if str(digital_pass).lower() == 'true':
            digital_pass = True
        elif str(digital_pass).lower() == 'false':
            digital_pass = False

        if str(rented_event).lower() == 'true':
            rented_event = True
        elif str(rented_event).lower() == 'false':
            rented_event = False

        if (event_name and event_details and event_venue and event_date_range and event_address and city and state and max_pass) is None:
            return Response(
            {
                "success": False,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": None,
                "error": "Missing required fields."
            }, status=status.HTTP_400_BAD_REQUEST)
        
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
                number_of_tickets=0,
                total_number_of_tickets=0
            )
            event_dates.append(current_date)
            current_date += timedelta(days=1)

        s3_bucket_folder = create_event_folders_s3(event_name=event_name, event_dates=event_dates)
        new_event = Event.objects.create(
            event_id=event_id,
            hod_id=hod_id,
            event_name=event_name,
            event_details=event_details,
            event_venue=event_venue,
            event_date_range=event_date_range,
            event_address=event_address,
            max_pass=max_pass,
            city=city,
            state=state,
            digital_pass=digital_pass,
            is_rented_event=rented_event,
            s3_bucket_folder=s3_bucket_folder,
            event_banner=event_banner
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
    def update(self, request, pk=None):
        event_id = pk
        if not event_id:
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
        event.event_address = request.data.get('event_address', event.event_address)
        event.city = request.data.get('city', event.city)
        event.state = request.data.get('state', event.state)

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


class EventTicketsViewSet(viewsets.ViewSet):
    
    @check_authentication()
    # @handle_exceptions
    def create(self, request):
        event_date_id = request.data.get('event_date_id')
        if not event_date_id:
            return Response(
                    {
                        "success": False,
                        "user_not_logged_in": False,
                        "user_unauthorized": False,                            
                        "data": None,
                        "error": "event_date_id required."
                    },
                    status=status.HTTP_400_BAD_REQUEST
                )

        event_date_data = EventDate.objects.filter(event_date_id=event_date_id).first()
        event_id = event_date_data.event_id

        event_data = Event.objects.filter(event_id=event_id).first()
        
        s3_bucket_folder = event_data.s3_bucket_folder
        # print(event_date_data.date)
        # event_date = datetime(event_date_data.date).strftime("%Y-%m-%d")

        ind = 0
        document_paths = []
        while True:
            if f'files[{ind}]' in request.FILES:
                document_paths.append(request.FILES[f'files[{ind}]'])
                ind+=1
            else:
                break

        event_date_folder = f"{s3_bucket_folder}{event_date_data.date} 00:00:00/Available Tickets"
        total_files_uploaded, error_files = upload_ticket_to_s3_event_folder(uploaded_files=document_paths, event_folder=event_date_folder)
        print(total_files_uploaded, error_files)
        data = {
            'total_files_uploaded': total_files_uploaded,
            'error_files': error_files
        }

        return Response(
                {
                    "success": True,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,                        
                    "data": data,
                    "error": None
                },
                status=status.HTTP_200_OK
            )        

    @check_authentication()
    @handle_exceptions
    def list(self, request):
        event_date_id = request.GET.get('event_date_id')
        if event_date_id:
            event_date_data = EventDate.objects.filter(event_date_id=event_date_id).first()
            event_id = event_date_data.event_id
            event_data = Event.objects.filter(event_id=event_id).first()
            
            s3_bucket_folder = event_data.s3_bucket_folder
            event_date = datetime(event_date_data.date).strftime("%Y-%m-%d")
            event_date_folder = f"{s3_bucket_folder}/{event_date}"
            
            total_tickets = get_number_of_tickets_in_event_folder(folder_name=event_date_folder)

        else:        
            event_data = Event.objects.filter(event_id=event_id).first()
            event_date_data = EventDate.objects.filter(event_id=event_id)
            
            total_tickets = 0
            
            s3_bucket_folder = event_data.s3_bucket_folder
            for event_date in event_date_data:
                date = datetime(event_date.date).strftime("%Y-%m-%d")
                event_date_folder = f"{s3_bucket_folder}/{date}"
                total_tickets += get_number_of_tickets_in_event_folder(folder_name=event_date_folder)

        data = {
            'total_tickets': total_tickets,
        }

        return Response(
                {
                    "success": True,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,                        
                    "data": data,
                    "error": None
                },
                status=status.HTTP_200_OK
            )        


class EventListViewSet(viewsets.ViewSet):
    @check_authentication()
    @handle_exceptions
    def list(self, request):
        if request.user.is_rented:
            event_id = request.user.rented_event_id
            events_obj = Event.objects.filter(event_id=event_id)
        else:
            events_obj = Event.objects.all()

        if request.user.role == 'reseller':
            events_data = ResellerEventsSerializer(events_obj, many=True, context={'seller_id': request.user}).data
        elif request.user.role == 'hod':
            events_data = HodEventsSerializer(events_obj, many=True).data
        
        data = {
            'events_data': events_data[::-1],
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
        

        if request.user.role == 'reseller':
            event_data = ResellerEventsSerializer(event_obj, context={'seller_id': request.user}).data
        elif request.user.role == 'hod':
            event_data = HodEventsSerializer(event_obj).data

        data = {
            "event_data": event_data,            
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class HodEventDateDetailViewSet(viewsets.ViewSet):
    @check_authentication('hod')
    @handle_exceptions
    def list(self, request):
        event_date_id = request.GET.get('event_date_id')
        if not event_date_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_date_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        event_date_obj = EventDate.objects.filter(event_date_id=event_date_id).first()
        if not event_date_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event Date not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_date_data = EventDateSerializer(event_date_obj).data

        event_obj = Event.objects.filter(event_id=event_date_obj.event_id).first()
        event_data = HodEventDateSerializer(event_obj, context={'event_date_id': event_date_id}).data

        reseller_obj = User.objects.filter(role='reseller')
        reseller_data = HodEventDateDetailUserSerializer(reseller_obj, context={'event_date_id': event_date_id}, many=True).data

        s3_bucket_folder = event_data['s3_bucket_folder']
        event_date_folder = f"{s3_bucket_folder}{event_date_data['date']} 00:00:00/Available Tickets"
        total_tickets_in_s3 = get_number_of_tickets_in_event_folder(folder_name=event_date_folder)
        # total_tickets_in_s3 = 0
        data = {
            "event_data": event_data,
            "event_date_data": event_date_data,
            
            "reseller_data": reseller_data[::-1],
            "len_reseller_data": len(reseller_data),   

            'total_tickets_in_s3': total_tickets_in_s3

        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class ResellerEventDateDetailViewSet(viewsets.ViewSet):
    @check_authentication('reseller')
    @handle_exceptions
    def list(self, request):
        event_date_id = request.GET.get('event_date_id')
        if not event_date_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_date_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        event_date_obj = EventDate.objects.filter(event_date_id=event_date_id).first()
        if not event_date_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event Date not found."
                }, status=status.HTTP_404_NOT_FOUND)
        
        event_date_data = EventDateSerializer(event_date_obj).data

        event_obj = Event.objects.filter(event_id=event_date_obj.event_id).first()
        event_data = ResellerEventDateSerializer(event_obj, context={'event_date_id': event_date_id, 'seller_id': request.user}).data

        data = {
            "event_data": event_data,
            "event_date_data": event_date_data,
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class TicketSaleEventDateDetailViewSet(viewsets.ViewSet):

    @handle_exceptions
    def list(self, request):
        event_date_id = request.GET.get('event_date_id')
        if not event_date_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event_date_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        seller_id = request.GET.get('seller_id')
        if not seller_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Seller_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        seller_data_obj = User.objects.filter(user_id=seller_id).first()
        if not seller_data_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Seller not found."
                }, status=status.HTTP_404_NOT_FOUND)

        event_date_obj = EventDate.objects.filter(event_date_id=event_date_id).first()
        if not event_date_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event Date not found."
                }, status=status.HTTP_404_NOT_FOUND)

        event_date_data = EventDateSerializer(event_date_obj).data

        event_obj = Event.objects.filter(event_id=event_date_obj.event_id).first()
        event_data = EventSerializer(event_obj).data

        seller_data = UserSerializer(seller_data_obj).data


        data = {
            "event_data": event_data,
            'event_date_data': event_date_data,
            "seller_data": seller_data,
        }

        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class TicketSaleEventDetailViewSet(viewsets.ViewSet):

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

        seller_id = request.GET.get('seller_id')
        if not seller_id:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Seller_id not provided."
                }, status=status.HTTP_404_NOT_FOUND)

        seller_data_obj = User.objects.filter(user_id=seller_id).first()
        if not seller_data_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Seller not found."
                }, status=status.HTTP_404_NOT_FOUND)

        event_obj = Event.objects.filter(event_id=event_id).first()
        if not event_obj:
            return Response(
                {
                    "success": False,
                    "user_not_logged_in": False,
                    "user_unauthorized": False,
                    "data": None,
                    "error": "Event Date not found."
                }, status=status.HTTP_404_NOT_FOUND)

        event_data = EventSerializer(event_obj).data
        seller_data = UserSerializer(seller_data_obj).data

        data = {
            "event_data": event_data,
            "seller_data": seller_data,
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


class HodDashboardDetailsViewSet(viewsets.ViewSet):

    @handle_exceptions
    @check_authentication(required_role='hod')
    def list(self, request):
        if request.user.is_rented:
            event_id = request.user.rented_event_id
            events_obj = Event.objects.filter(event_id=event_id)
            events_data = HodDashboardEventSerializer(events_obj, many=True).data

            reseller_obj = User.objects.filter(role='reseller', is_rented=True, rented_event_id=event_id)
            reseller_data = HodDashboardUserSerializer(reseller_obj, many=True).data

            all_ticket_obj = Ticket.objects.filter(event_id=event_id)
            all_ticket_data = HodTicketSerializer(all_ticket_obj, many=True).data

            all_ticket_data_qty_amt = QtyAmountTicketSerializer(all_ticket_obj, many=True).data

            all_tickets_sold = 0
            all_tickets_sold_amount = 0

            for ticket_sold in all_ticket_data_qty_amt:
                all_tickets_sold+=ticket_sold['qty']
                all_tickets_sold_amount+=ticket_sold['amount']


            data = {
                'events_data': events_data[::-1],
                'len_events_data': len(events_data),

                'reseller_data': reseller_data[::-1],
                'len_reseller_data': len(reseller_data),

                'all_ticket_data': all_ticket_data,
                'len_all_ticket_data': len(all_ticket_data),

                'all_tickets_sold': all_tickets_sold,
                'all_tickets_sold_amount': all_tickets_sold_amount,
            }

        else:
            events_obj = Event.objects.all()
            events_data = HodDashboardEventSerializer(events_obj, many=True).data

            reseller_obj = User.objects.filter(role='reseller')
            reseller_data = HodDashboardUserSerializer(reseller_obj, many=True).data

            all_ticket_obj = Ticket.objects.all()
            all_ticket_data = HodTicketSerializer(all_ticket_obj, many=True).data

            all_ticket_data_qty_amt = QtyAmountTicketSerializer(all_ticket_obj, many=True).data

            all_tickets_sold = 0
            all_tickets_sold_amount = 0

            for ticket_sold in all_ticket_data_qty_amt:
                all_tickets_sold+=ticket_sold['qty']
                all_tickets_sold_amount+=ticket_sold['amount']


            data = {
                'events_data': events_data[::-1],
                'len_events_data': len(events_data),

                'reseller_data': reseller_data[::-1],
                'len_reseller_data': len(reseller_data),

                'all_ticket_data': all_ticket_data,
                'len_all_ticket_data': len(all_ticket_data),

                'all_tickets_sold': all_tickets_sold,
                'all_tickets_sold_amount': all_tickets_sold_amount,
            }


        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)


class ResellerDashboardDetailsViewSet(viewsets.ViewSet):

    @handle_exceptions
    # @check_authentication(required_role='hod')
    def list(self, request):
        if request.user.is_rented:
            event_id = request.user.rented_event_id

            events_obj = Event.objects.filter(event_id=event_id)
            events_data = ResellerDashboardEventSerializer(events_obj, many=True, context={'seller_id': request.user}).data

            all_ticket_obj = Ticket.objects.filter(seller_id=request.user)
            all_ticket_data = HodTicketSerializer(all_ticket_obj, many=True).data

            all_ticket_data_qty_amt = QtyAmountTicketSerializer(all_ticket_obj, many=True).data

            all_tickets_sold = 0
            all_tickets_sold_amount = 0

            for ticket_sold in all_ticket_data_qty_amt:
                all_tickets_sold+=ticket_sold['qty']
                all_tickets_sold_amount+=ticket_sold['amount']


            data = {
                'events_data': events_data,
                'len_events_data': len(events_data),

                'all_ticket_data': all_ticket_data,
                'len_all_ticket_data': len(all_ticket_data),

                'all_tickets_sold': all_tickets_sold,
                'all_tickets_sold_amount': all_tickets_sold_amount,
            }

        else:

            events_obj = Event.objects.all()
            events_data = ResellerDashboardEventSerializer(events_obj, many=True, context={'seller_id': request.user}).data

            all_ticket_obj = Ticket.objects.filter(seller_id=request.user)
            all_ticket_data = HodTicketSerializer(all_ticket_obj, many=True).data

            all_ticket_data_qty_amt = QtyAmountTicketSerializer(all_ticket_obj, many=True).data

            all_tickets_sold = 0
            all_tickets_sold_amount = 0

            for ticket_sold in all_ticket_data_qty_amt:
                all_tickets_sold+=ticket_sold['qty']
                all_tickets_sold_amount+=ticket_sold['amount']


            data = {
                'events_data': events_data,
                'len_events_data': len(events_data),

                'all_ticket_data': all_ticket_data,
                'len_all_ticket_data': len(all_ticket_data),

                'all_tickets_sold': all_tickets_sold,
                'all_tickets_sold_amount': all_tickets_sold_amount,
            }


        return Response(
            {
                "success": True,
                "user_not_logged_in": False,
                "user_unauthorized": False,
                "data": data,
                "error": None
            }, status=status.HTTP_200_OK)

