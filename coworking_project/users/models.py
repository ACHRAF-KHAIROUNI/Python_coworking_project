# users/models.py

from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    ROLE_CHOICES = (
        ('CEO', 'CEO'),
        ('ADMIN', 'Admin'),
        ('USER', 'User'),
    )
    # On ne redéfinit pas nom, prenom, email car ils sont déjà dans AbstractUser
    # On ajoute nos champs spécifiques
    role = models.CharField(max_length=5, choices=ROLE_CHOICES, default='USER', verbose_name="Rôle")
    etat = models.BooleanField(default=False, verbose_name="Compte activé")
    solde = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    rfid = models.CharField(max_length=100, null=True, blank=True, unique=True)

    def __str__(self):
        return self.username