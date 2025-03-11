import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from utils.decorators import *

from Event.models import *


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
            return render(request, 'hod/dashboard.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/dashboard.html')


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

