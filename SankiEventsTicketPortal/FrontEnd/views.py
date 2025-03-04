import random
import string
from datetime import datetime, timedelta

from rest_framework import viewsets, status
from rest_framework.response import Response

from django.shortcuts import render, get_object_or_404, redirect
from django.http import HttpResponse

from utils.decorators import *


class DashboardFrontEndViewSet(viewsets.ViewSet):
    def list(self, request):
        user = request.user
        if not user.is_authenticated:
            return HttpResponse('Not logged in')
        # if user.role == 'hod':
        if user.role == 'admin':
            return render(request, 'hod/dashboard.html')
        
        elif user.role == 'reseller':
            return render(request, 'reseller/dashboard.html')
