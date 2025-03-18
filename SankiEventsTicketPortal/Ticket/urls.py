from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'ticket-api', TicketViewSet, basename='ticket-api')
router.register(r'get-all-ticket-api', AllTicketViewSet, basename='get-all-ticket-api')
router.register(r'approve-ticket-api', ApproveTicketViewSet, basename='approve-ticket-api')
router.register(r'send-ticket-mail-api', SendTicketMailViewSet, basename='send-ticket-mail-api')

router.register(r'assign-ticket-api', AssignTicketViewSet, basename='assign-ticket-api')

urlpatterns = [
    path('', include(router.urls))
]
