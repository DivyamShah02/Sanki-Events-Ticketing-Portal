from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()
router.register(r'event-api', EventViewSet, basename='event-api')
router.register(r'event-ticket-api', EventTicketsViewSet, basename='event-ticket-api')
router.register(r'all-events-api', EventListViewSet, basename='all-events-api')
router.register(r'event-data-api', EventDetailViewSet, basename='event-data-api')

router.register(r'update-ticket-api', TicketUpdateViewSet, basename='update-ticket-api')

router.register(r'hod-dashboard-api', HodDashboardDetailsViewSet, basename='hod-dashboard-api')

urlpatterns = [
    path('', include(router.urls))
]
