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
        if user.role == 'hod':
            data = {
                'sellers': User.objects.filter(role='reseller'),
                'events': Event.objects.all().order_by('-event_id'),
            }
            return render(request, 'hod/dashboard.html', data)
        
        elif user.role == 'reseller':
            data = {
                'events': Event.objects.all().order_by('-event_id'),
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
            return render(request, 'hod/event_date_detail.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/event_date_detail.html')


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
            return render(request, 'hod/event_qr_scanner.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/event_date_detail.html')
