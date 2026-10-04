# my_coworking_project/urls.py
from django.contrib import admin
from django.urls import path, include
from company.views import home_view
from my_coworking_project import settings 
from django.conf.urls.static import static

urlpatterns = [
    path('', home_view, name='home'),
    path('admin/', admin.site.urls),
    path('accounts/', include('users.urls')), # Inclut toutes les URLs de l'app 'users'
    path('gestion/', include('company.urls', namespace='company')), # Inclut toutes les URLs de l'app 'company'
    path('reservations/', include(('reservations.urls', 'reservations'), namespace='reservations')),

    path('chat/', include('chatAI.urls')),
    path('twilio/', include('twilio_chatbot.urls')),

    path('api/', include('api.urls')),
]

if settings.DEBUG and hasattr(settings, 'MEDIA_ROOT'):
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)