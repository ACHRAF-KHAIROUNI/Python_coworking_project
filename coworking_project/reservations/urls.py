# reservations/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('mes-reservations/', views.MesReservationsView.as_view(), name='mes_reservations'),
    path('annuler/<int:pk>/', views.annuler_reservation, name='annuler_reservation'),
    path('repayer/<int:pk>/', views.reessayer_paiement, name='reessayer_paiement'),

    path('gestion/', views.GestionReservationsView.as_view(), name='gestion_reservations'),
    path('gestion/annuler/<int:pk>/', views.annuler_reservation_admin, name='annuler_reservation_admin'),

    path('commentaire/<int:reservation_id>/', views.laisser_commentaire_view, name='laisser_commentaire'),
]