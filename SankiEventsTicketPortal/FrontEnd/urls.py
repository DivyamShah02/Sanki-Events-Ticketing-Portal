from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import *


router = DefaultRouter()

router.register(r'', HomeViewSet, basename='home')

router.register(r'login', LoginViewSet, basename='login')
router.register(r'dashboard', DashboardFrontEndViewSet, basename='dashboard')
router.register(r'events', EventsFrontEndViewSet, basename='events')
router.register(r'event_detail', EventDetailFrontEndViewSet, basename='event_detail')
router.register(r'event_date_detail', EventDateDetailFrontEndViewSet, basename='event_date_detail')

urlpatterns = [
    path('', include(router.urls))
]
