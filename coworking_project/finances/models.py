# finances/models.py
from django.db import models
from django.conf import settings

class RechargeSolde(models.Model):
    code = models.CharField(max_length=50, unique=True, verbose_name="Code de recharge")
    solde = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Montant")
    etat_consommation = models.ForeignKey(
        settings.AUTH_USER_MODEL, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        verbose_name="Consommé par"
    )
    date_creation = models.DateTimeField(auto_now_add=True)
    date_consommation = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        status = "Disponible"
        if self.etat_consommation:
            status = f"Utilisé par {self.etat_consommation.username}"
        return f"Code {self.code} ({self.solde}€) - {status}"