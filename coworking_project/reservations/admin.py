# reservations/admin.py
from django.contrib import admin
from .models import Reservation
from .models import Reservation, Commentaire

@admin.register(Reservation)
class ReservationAdmin(admin.ModelAdmin):
    list_display = ('salle', 'user', 'date_reservation', 'heure_debut', 'heure_fin', 'etat')
    list_filter = ('etat', 'date_reservation', 'salle')
    search_fields = ('user__username', 'salle__nom')
    

admin.site.register(Commentaire)