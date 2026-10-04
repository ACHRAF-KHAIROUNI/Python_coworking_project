# users/admin.py

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User

# Nous créons une classe qui hérite de UserAdmin pour la personnaliser
class CustomUserAdmin(UserAdmin):
    # fieldsets est la structure de la page d'édition d'un utilisateur
    # On copie la structure existante de UserAdmin et on y ajoute notre champ 'role'
    
    # Copiez les fieldsets de la classe parente
    fieldsets = list(UserAdmin.fieldsets)

    # Ajoutez votre propre fieldset (groupe de champs) pour les informations personnalisées
    # Nous l'ajoutons en deuxième position pour qu'il apparaisse après les infos personnelles
    fieldsets.insert(1, ('Informations Personnalisées', {'fields': ('role', 'solde', 'etat', 'rfid')}))

    # Si vous voulez aussi voir ces champs dans la liste des utilisateurs
    # (et pas seulement dans le formulaire de modification)
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff', 'role', 'etat')


# Annulez l'enregistrement précédent si vous l'aviez
# admin.site.unregister(User) # Pas nécessaire si vous éditez le fichier la première fois

# Enregistrez votre modèle User avec la classe d'admin personnalisée
admin.site.register(User, CustomUserAdmin)