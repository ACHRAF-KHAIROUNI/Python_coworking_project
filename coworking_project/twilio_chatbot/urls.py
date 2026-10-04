# twilio_chatbot/urls.py

from django.urls import path
from . import views

urlpatterns = [
    # C'est l'URL de notre webhook
    path('webhook/', views.twilio_webhook, name='twilio_webhook'),
]