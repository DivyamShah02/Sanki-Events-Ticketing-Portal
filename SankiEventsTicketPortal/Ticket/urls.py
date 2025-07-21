from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'ticket-api', TicketViewSet, basename='ticket-api')
router.register(r'sell-event-ticket-api', EventTicketViewSet, basename='sell-event-ticket-api')

router.register(r'get-all-ticket-api', AllTicketViewSet, basename='get-all-ticket-api')
router.register(r'approve-ticket-api', ApproveTicketViewSet, basename='approve-ticket-api')
router.register(r'send-ticket-mail-api', SendTicketMailViewSet, basename='send-ticket-mail-api')
router.register(r're-send-ticket-mail-api', ReSendTicketMailViewSet, basename='re-send-ticket-mail-api')
router.register(r'decline-ticket-api', DeclineTicketViewSet, basename='decline-ticket-api')

router.register(r'assign-ticket-api', AssignTicketViewSet, basename='assign-ticket-api')
router.register(r'add-available-ticket-api', AddAvailableTicketsViewSet, basename='add-available-ticket-api')

router.register(r'export-assigned-ticket-api', AdminExportAssignedTicketDataViewSet, basename='export-assigned-ticket-api')

router.register(r'ticket-pass-api', TicketPassViewSet, basename='ticket-pass-api')
router.register(r'validate-ticket-pass-api', ValidateTicketPassViewSet, basename='validate-ticket-pass-api')

router.register(r'export-ticket', TicketExportViewSet, basename='export-ticket')

urlpatterns = [
    path('', include(router.urls))
]
