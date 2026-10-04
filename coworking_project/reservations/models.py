# reservations/models.py
from django.db import models
from django.conf import settings

from django.core.validators import MinValueValidator, MaxValueValidator

class Reservation(models.Model):
    STATE_CHOICES = (
        ('CONFIRMED', 'Confirmée'),
        ('PENDING', 'En attente'),
        ('LOCKED', 'Verrouillée'),   # <-- NOUVEAU
        ('COMPLETED', 'Terminée'),   # <-- NOUVEAU
        ('CANCELLED', 'Annulée'),
    )

    salle = models.ForeignKey('company.Salle', on_delete=models.CASCADE, related_name='reservations')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='reservations')
    
    date_reservation = models.DateField(verbose_name="Date de la réservation")
    heure_debut = models.TimeField(verbose_name="Heure de début")
    heure_fin = models.TimeField(verbose_name="Heure de fin")

    etat = models.CharField(max_length=10, choices=STATE_CHOICES, default='PENDING')
    prix_total = models.DecimalField(max_digits=10, decimal_places=2)
    
    date_creation = models.DateTimeField(auto_now_add=True)
    # On pourrait ajouter ici les champs du paiement si on voulait les tracer
    # code_reduction_applique = models.ForeignKey('finances.CodeReduction', null=True, blank=True, on_delete=models.SET_NULL)

    def __str__(self):
        return f"Réservation de {self.salle.nom} par {self.user.username} le {self.date_reservation}"
    

class Commentaire(models.Model):
    # La relation vers Reservation est OK car elle est dans le même fichier
    reservation = models.OneToOneField(
        Reservation,
        on_delete=models.CASCADE,
        verbose_name="Réservation associée"
    )
    note = models.PositiveIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        verbose_name="Note (sur 5)"
    )
    texte = models.TextField(verbose_name="Commentaire")
    date_creation = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-date_creation']

    def __str__(self):
        return f"Avis de {self.reservation.user.username} pour {self.reservation.salle.nom}"
    
