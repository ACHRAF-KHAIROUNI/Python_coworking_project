# api/urls.py

from django.urls import path
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
from .views import (
    ReservationListView,
    CompleteReservationView,
    CancelReservationView,
    SalleListView
    )

urlpatterns = [
    # L'admin enverra un POST avec "username" et "password" à cette URL
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    
    # Pour rafraîchir un token qui a expiré (fonctionnalité avancée)
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('reservations/', ReservationListView.as_view(), name='reservation-list'),
    path('reservations/<int:pk>/complete/', CompleteReservationView.as_view(), name='reservation-complete'),
    path('reservations/<int:pk>/cancel/', CancelReservationView.as_view(), name='reservation-cancel'),
    path('salles/', SalleListView.as_view(), name='salle-list'),

]