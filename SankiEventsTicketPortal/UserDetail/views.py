from rest_framework.response import Response
from rest_framework import status
from rest_framework import viewsets
from rest_framework.exceptions import NotFound, ParseError

from django.shortcuts import get_object_or_404, render, redirect
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponse, JsonResponse

from .serializers import UserSerializer
from .models import User

import random
import string
from datetime import datetime, timedelta

from utils.decorators import *

logger = None


class UserViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    @check_authentication(required_role='admin')
    def create(self, request):
            name = request.data.get('name')
            password = request.data.get('password')
            contact_number = request.data.get('contact_number')
            email = request.data.get('email')
            role = request.data.get('role')            

            role_codes = {
                'admin': 'AD',
                'hod': 'HO',
                'reseller': 'RE'
            }

            email_already_user = User.objects.filter(email=email).first()
            contact_number_already_user = User.objects.filter(contact_number=contact_number).first()

            if email_already_user or contact_number_already_user:
                return Response(
                        {
                            "success": False,                            
                            "user_not_logged_in": False,
                            "user_unauthorized": False,
                            "data":None,
                            "error": "User already registered."
                        }, status=status.HTTP_400_BAD_REQUEST)

            if not name or not contact_number or not email or role not in role_codes.keys():
                return Response(
                        {
                            "success": False,                            
                            "user_not_logged_in": False,
                            "user_unauthorized": False,
                            "data":None,
                            "error": "Missing required fields."
                        }, status=status.HTTP_400_BAD_REQUEST)


            user_id = self.generate_user_id(role_code=role_codes[role])

            if str(role_codes[role]) == 'AD':
                user = User.objects.create_superuser(
                    user_id=user_id,
                    username = user_id,
                    password = password,
                    email=email,
                    name=name,
                    contact_number=contact_number,
                    role=role,
                )
            
            else:
                user = User.objects.create_user(
                    user_id=user_id,
                    username = user_id,
                    password = password,
                    email=email,
                    name=name,
                    contact_number=contact_number,
                    role=role,
                )
            
            user_detail_serializer = UserSerializer(user)
            user_data = user_detail_serializer.data

            return Response(
                        {
                            "success": True,  
                            "user_not_logged_in": False,
                            "user_unauthorized": False,                       
                            "data": user_data,
                            "error": None
                        }, status=status.HTTP_201_CREATED)

    @handle_exceptions
    @check_authentication
    def list(self, request):
        user_id = request.query_params.get('user_id')  # Use query_params for GET requests
        if not user_id:
            return Response(
                        {
                            "success": False,
                            "user_not_logged_in": False,
                            "user_unauthorized": False,
                            "data": None,
                            "error": "Missing user_id."
                        }, status=status.HTTP_400_BAD_REQUEST)

        user_data_obj = get_object_or_404(User, user_id=user_id)
        user_data = UserSerializer(user_data_obj).data
        return Response(
                    {
                        "success": True,
                        "user_not_logged_in": False,
                        "user_unauthorized": False,
                        "data": user_data,
                        "error": None
                    }, status=status.HTTP_200_OK)

    def generate_user_id(self, role_code):
        while True:
            user_id = ''.join(random.choices(string.digits, k=10))
            user_id = role_code + user_id
            if not User.objects.filter(user_id=user_id).exists():
                return user_id


class LoginApiViewSet(viewsets.ViewSet):
    
    @handle_exceptions
    def create(self, request):
        email = request.data.get('email')
        password = request.data.get('password')

        if not email or not password:
            return Response(
                {
                    "success": False,
                    "user_does_not_exist": False,
                    "wrong_password": False,
                    "error": "Email and password are required."
                },
                status=status.HTTP_400_BAD_REQUEST
            )

        user = User.objects.filter(email=email).first()
        if not user:
            return Response(
                {
                    "success": False,
                    "user_does_not_exist": True,
                    "wrong_password": False,
                    "error": None
                }, status=status.HTTP_404_NOT_FOUND)

        authenticated_user = authenticate(request, username=user.user_id, password=password)
        if not authenticated_user:
            return Response(
                {
                    "success": False,
                    "user_does_not_exist": False,
                    "wrong_password": True,
                    "error": None
                }, status=status.HTTP_401_UNAUTHORIZED)

        login(request, authenticated_user)
        request.session.set_expiry(30 * 24 * 60 * 60)

        return Response(
            {
                "success": True,
                "user_does_not_exist": False,
                "wrong_password": False,
                "error": None,
                "data": {"user_id": user.username}
            }, status=status.HTTP_200_OK)


class LogoutApiViewSet(viewsets.ViewSet):
    def list(self, request):
        try:
            logout(request)
            return HttpResponse('DONE')
            return redirect('dashboard-list')

        except Exception as e:
            print(e)
            return HttpResponse('DONE')
            return redirect('dashboard-list')


def login_to_account(request):
    try:
        request_user = request.user
        username = request.GET.get('username')
        print(username)

        user = User.objects.get(username=username)

        if request_user.is_staff:
            print('Staff')
            login(request, user)

        return HttpResponse('DONE')
        return redirect('dashboard-list')

    except Exception as e:
        print(e)
        return HttpResponse('DONE')
        return redirect('dashboard-list')
