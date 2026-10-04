# api/serializers.py
from rest_framework import serializers
from reservations.models import Reservation
from users.models import User
from company.models import Salle

# Un serializer simple pour afficher les infos de base du client
class ClientSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']

# Un serializer simple pour afficher le nom de la salle
class SalleSerializer(serializers.ModelSerializer):
    class Meta:
        model = Salle
        fields = ['id', 'nom']

# Le serializer principal pour les réservations
class ReservationSerializer(serializers.ModelSerializer):
    # On utilise les serializers ci-dessus pour afficher des objets imbriqués lisibles
    user = ClientSerializer(read_only=True)
    salle = SalleSerializer(read_only=True)

    class Meta:
        model = Reservation
        # On choisit les champs qu'on veut exposer dans l'API
        fields = [
            'id', 
            'user', 
            'salle', 
            'date_reservation', 
            'heure_debut', 
            'heure_fin', 
            'etat', 
            'prix_total'
        ]