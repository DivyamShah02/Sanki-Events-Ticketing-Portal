from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    # path('favicon.ico', RedirectView.as_view(url='/static/logo.png')),

    path('', include('FrontEnd.urls')),
    path('user/', include('UserDetail.urls')),
    path('event/', include('Event.urls')),
    path('ticket/', include('Ticket.urls')),

]+static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
