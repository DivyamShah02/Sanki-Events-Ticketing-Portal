import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from utils.decorators import *

from Event.models import *
from UserDetail.models import User

class HomeViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')
        
        else:
            return redirect('dashboard-list')


class LoginViewSet(viewsets.ViewSet):
    def list(self, request):
        return render(request, 'login.html')


class DashboardFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')
            return HttpResponse('Not logged in')
        # if user.role == 'admin':
        is_rented = False
        if user.role == 'hod':
            if request.user.is_rented:
                is_rented = True
                event_id = request.user.rented_event_id
                events_obj = Event.objects.filter(event_id=event_id)
                seller_data = User.objects.filter(role='reseller', rented_event_id=event_id)
            else:
                events_obj = Event.objects.all()
                seller_data = User.objects.filter(role='reseller')

            data = {
                'sellers': seller_data,
                'events': events_obj.order_by('-event_id'),
                'is_rented': is_rented
            }
            return render(request, 'hod/dashboard.html', data)
        
        elif user.role == 'reseller':
            if request.user.is_rented:
                is_rented = True
                event_id = request.user.rented_event_id
                events_obj = Event.objects.filter(event_id=event_id)
            
            else:
                events_obj = Event.objects.all()

            data = {
                'events': events_obj.order_by('-event_id'),
                'is_rented': is_rented
            }
            return render(request, 'reseller/dashboard.html', data)


class EventsFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')
            return HttpResponse('Not logged in')
        # if user.role == 'admin':
        if user.role == 'hod':
            return render(request, 'hod/events.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/events.html')


class EventDetailFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')

        if not request.GET.get('event_id'):
            return redirect('events-list')
        
        event_data = Event.objects.filter(event_id=request.GET.get('event_id')).first()
        if not event_data:
            return redirect('events-list')

        if user.role == 'hod':
            return render(request, 'hod/event_detail.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/event_detail.html')


class EventDateDetailFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')

        if not request.GET.get('event_date_id'):
            return redirect('events-list')

        event_data = EventDate.objects.filter(event_date_id=request.GET.get('event_date_id')).first()
        if not event_data:
            return redirect('events-list')

        if user.role == 'hod':
            return render(request, 'hod/event_date_detail.html', {"event_date_id": request.GET.get('event_date_id')})

        elif user.role == 'reseller':
            return render(request, 'reseller/event_date_detail.html', {"event_date_id": request.GET.get('event_date_id')})


class TicketSaleFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        return render(request, 'ticket_sale.html')


class EventTicketSaleFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            seller_id = request.GET.get('seller_id')
            user_data = User.objects.filter(user_id=seller_id).first()
            
            company_logo = user_data.company_logo if user_data.company_logo else ""
            
            data = {
                'company_logo': company_logo,
            }
        except:
            data = {
                'company_logo': "",
            }    
        return render(request, 'event_ticket_sale.html', data)


class EventQrCodeFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return redirect('login-list')

        if user.role == 'hod':
            return render(request, 'hod/event_qr_scanner.html', {"event_date_id": request.GET.get('event_date_id')})
        
        elif user.role == 'reseller':
            return render(request, 'reseller/event_date_detail.html')
