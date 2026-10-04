# finances/admin.py
from django.contrib import admin
from .models import RechargeSolde

@admin.register(RechargeSolde)
class RechargeSoldeAdmin(admin.ModelAdmin):
    list_display = ('code', 'solde', 'etat_consommation', 'date_consommation')
    list_filter = ('etat_consommation',)
    search_fields = ('code',)