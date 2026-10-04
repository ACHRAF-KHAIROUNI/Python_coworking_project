# api/views.py
from rest_framework.generics import ListAPIView
from reservations.models import Reservation
from company.models import Administrateur
from .serializers import ReservationSerializer
from .permissions import IsAdminOfAssociatedCompany
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from django.utils import timezone
from datetime import datetime, timedelta
from django.core.mail import EmailMessage
from django.template.loader import render_to_string
from company.models import Salle
from .serializers import SalleSerializer

class ReservationListView(ListAPIView):
    serializer_class = ReservationSerializer
    # On applique notre permission personnalisée
    permission_classes = [IsAdminOfAssociatedCompany] 

    def get_queryset(self):
        # On récupère l'objet admin lié à l'utilisateur qui fait la requête
        admin_profile = Administrateur.objects.get(user=self.request.user)
        societe_admin = admin_profile.societe
        
        # On filtre les réservations pour ne retourner que celles de sa société
        queryset = Reservation.objects.filter(salle__societer=societe_admin)

        # --- Logique de filtrage par paramètres GET ---
        date_filter = self.request.query_params.get('date', None)
        salle_id_filter = self.request.query_params.get('salle_id', None)

        if date_filter:
            queryset = queryset.filter(date_reservation=date_filter)
        if salle_id_filter:
            queryset = queryset.filter(salle_id=salle_id_filter)

        return queryset.order_by('date_reservation', 'heure_debut')
    

class CompleteReservationView(APIView):
    permission_classes = [IsAdminOfAssociatedCompany]

    def post(self, request, pk, format=None):
        # L'admin envoie un POST sur /api/reservations/<pk>/complete/
        admin_profile = Administrateur.objects.get(user=request.user)
        
        # On cherche la réservation, en s'assurant qu'elle appartient bien à la société de l'admin
        reservation = get_object_or_404(
            Reservation, 
            pk=pk, 
            salle__societer=admin_profile.societe
        )

        # On ne peut "compléter" qu'une réservation confirmée
        if reservation.etat != 'CONFIRMED':
            return Response(
                {'error': f"Impossible de compléter une réservation qui est à l'état '{reservation.get_etat_display()}'."},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        reservation.etat = 'COMPLETED'
        reservation.save()
        
        # --- ENVOI EMAIL ---
        client = reservation.user
        mail_subject = "Merci d'avoir utilisé nos services !"
        message = render_to_string('api/emails/email_reservation_completee.html', {
            'user': client,
            'reservation': reservation
        })
        email = EmailMessage(mail_subject, message, to=[client.email])
        email.content_subtype = "html"
        email.send()
        
        serializer = ReservationSerializer(reservation)
        return Response(serializer.data, status=status.HTTP_200_OK)
    

class CancelReservationView(APIView):
    permission_classes = [IsAdminOfAssociatedCompany]

    def post(self, request, pk, format=None):
        admin_profile = Administrateur.objects.get(user=request.user)
        reservation = get_object_or_404(Reservation, pk=pk, salle__societer=admin_profile.societe)

        if reservation.etat not in ['CONFIRMED', 'PENDING']:
            return Response(
                {'error': "Seules les réservations confirmées ou en attente peuvent être annulées."},
                status=status.HTTP_400_BAD_REQUEST
            )

        # --- Logique de remboursement conditionnel ---
        remboursement_effectue = False
        temps_restant = timezone.make_aware(datetime.combine(reservation.date_reservation, reservation.heure_debut)) - timezone.now()

        if temps_restant > timedelta(hours=24):
            # Plus de 24h restantes -> Remboursement
            client = reservation.user
            ceo = reservation.salle.societer.ceo
            
            client.solde += reservation.prix_total
            if ceo:
                ceo.solde -= reservation.prix_total
            
            client.save()
            if ceo:
                ceo.save()
            
            remboursement_effectue = True

        reservation.etat = 'CANCELLED'
        reservation.save()

         # --- ENVOI EMAIL ---
        client = reservation.user
        mail_subject = f"Information concernant votre réservation pour la salle {reservation.salle.nom}"
        message = render_to_string('api/emails/email_admin_annulation.html', {
            'user': client,
            'reservation': reservation,
            'remboursement': remboursement_effectue # On passe cette variable au template
        })
        email = EmailMessage(mail_subject, message, to=[client.email])
        email.content_subtype = "html"
        email.send()
        
        message = "Réservation annulée."
        if remboursement_effectue:
            message += " Le client a été remboursé sur son solde."
        else:
            message += " Aucun remboursement effectué (moins de 24h restantes)."

        return Response({'success': message}, status=status.HTTP_200_OK)
    

class SalleListView(ListAPIView):
    serializer_class = SalleSerializer
    permission_classes = [IsAdminOfAssociatedCompany] # Seul un admin de la société peut voir les salles

    def get_queryset(self):
        # On récupère le profil admin et sa société
        admin_profile = Administrateur.objects.get(user=self.request.user)
        societe_admin = admin_profile.societe
        
        # On retourne uniquement les salles de cette société
        return Salle.objects.filter(societer=societe_admin).order_by('nom')