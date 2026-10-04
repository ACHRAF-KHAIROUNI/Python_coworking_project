# company/models.py

from django.db import models
from django.conf import settings # Pour référencer le modèle User de manière sécurisée


from reservations.models import Reservation



class Societer(models.Model):
    STATE_CHOICES = (
        ('PENDING', 'En attente'),
        ('ACTIVE', 'Active'),
        ('REJECTED', 'Refusée'),
    )
    nom = models.CharField(max_length=255)
    numero_patante = models.CharField(max_length=255, unique=True)
    description = models.TextField()
    email = models.EmailField()
    localisation = models.CharField(max_length=255, verbose_name="Adresse de la société")
    vote = models.FloatField(default=0.0)
    etat = models.CharField(max_length=10, choices=STATE_CHOICES, default='PENDING')
    # OneToOneField garantit qu'un utilisateur ne peut être CEO que d'UNE seule société
    ceo = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name="societe_dirigee")

    def __str__(self):
        return self.nom

class Materiel(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    categorie = models.CharField(max_length=100)

    def __str__(self):
        return self.nom

class Salle(models.Model):
    nom = models.CharField(max_length=255)
    capacite = models.PositiveIntegerField(verbose_name="Capacité")
    description = models.TextField()
    prix_par_heure = models.DecimalField(max_digits=10, decimal_places=2)
    latitude = models.FloatField(null=True, blank=True)
    longitude = models.FloatField(null=True, blank=True)
    societer = models.ForeignKey(Societer, on_delete=models.CASCADE, related_name="salles")
    vote = models.FloatField(default=0.0)
    heurD = models.TimeField(verbose_name="Heure d'ouverture")
    heurF = models.TimeField(verbose_name="Heure de fermeture")
    # On ajoute le lien vers le matériel via la table de liaison
    materiels = models.ManyToManyField(Materiel, through='SalleMateriel')

    def __str__(self):
        return f"{self.nom} ({self.societer.nom})"

class SalleMateriel(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE)
    materiel = models.ForeignKey(Materiel, on_delete=models.CASCADE)
    quantite = models.PositiveIntegerField(default=1)

    class Meta:
        # Garantit qu'on ne peut pas ajouter le même matériel deux fois à la même salle
        unique_together = ('salle', 'materiel')

    def __str__(self):
        return f"{self.quantite} x {self.materiel.nom} dans {self.salle.nom}"

class ImageSalle(models.Model):
    salle = models.ForeignKey(Salle, on_delete=models.CASCADE, related_name='images')
    image = models.URLField(max_length=500)
    legende = models.CharField(max_length=255, blank=True, verbose_name="Légende")

    def __str__(self):
        return f"Image pour la salle {self.salle.nom}"
    

class Administrateur(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="Utilisateur"
    )
    societe = models.ForeignKey(
        Societer,
        on_delete=models.CASCADE,
        verbose_name="Société administrée"
    )
    date_nomination = models.DateTimeField(auto_now_add=True)

    class Meta:
        # Un utilisateur ne peut être admin que pour une seule société à la fois.
        # C'est garanti par le OneToOneField sur le user.
        # Si vous vouliez qu'un user soit admin de plusieurs sociétés,
        # vous remplaceriez OneToOneField par ForeignKey et ajouteriez :
        # unique_together = ('user', 'societe')
        verbose_name = "Administrateur"
        verbose_name_plural = "Administrateurs"

    def __str__(self):
        return f"{self.user.username} est admin de {self.societe.nom}"
    
