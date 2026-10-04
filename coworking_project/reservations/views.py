# reservations/views.py

import uuid
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from datetime import datetime, timedelta, timezone
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from finances.models import RechargeSolde
from django.views.generic import ListView

from users.mixins import AdminRoleRequiredMixin

from .forms import ReservationForm
from .models import Commentaire, Reservation
from company.models import Salle

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from django.db import transaction # N'oubliez pas cet import !
from users.models import User

# reservations/views.py
from django.db import transaction # N'oubliez pas cet import !
from users.models import User # Importez le modèle User pour le get_object_or_404

from django.db.models import Avg
from .forms import CommentaireForm

# ... autres imports ...

def salle_detail_and_reservation_view(request, pk):
    salle = get_object_or_404(Salle, pk=pk, societer__etat='ACTIVE')
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
            
        form = ReservationForm(request.POST)
        if form.is_valid():
            data = form.cleaned_data
            date_reserv = data['date_reservation']
            heure_debut = data['heure_debut']
            duree = data['duree_heures']

            # ... (Toute votre logique de validation de créneau, qui est correcte) ...
            heure_fin = (datetime.combine(date_reserv, heure_debut) + timedelta(hours=duree)).time()
            if not (salle.heurD <= heure_debut < salle.heurF and salle.heurD < heure_fin <= salle.heurF):
                messages.error(request, "Le créneau demandé est en dehors des heures d'ouverture de la salle.")
                return redirect('company:salle_detail', pk=salle.pk)
            reservations_ce_jour = Reservation.objects.filter(salle=salle, date_reservation=date_reserv, etat='CONFIRMED')
            creneau_debut = datetime.combine(date_reserv, heure_debut)
            creneau_fin = datetime.combine(date_reserv, heure_fin)
            is_disponible = True
            for res in reservations_ce_jour:
                res_debut = datetime.combine(date_reserv, res.heure_debut)
                res_fin_occupation = (datetime.combine(date_reserv, res.heure_fin) + timedelta(minutes=30))
                if creneau_debut < res_fin_occupation and creneau_fin > res_debut:
                    is_disponible = False
                    break
            if not is_disponible:
                messages.error(request, "Désolé, ce créneau n'est pas disponible.")
                return redirect('company:salle_detail', pk=salle.pk)
            # --- Fin de la validation du créneau ---

            prix_total = salle.prix_par_heure * duree
            
            reservation_instance = Reservation(
                salle=salle, user=request.user, date_reservation=date_reserv,
                heure_debut=heure_debut, heure_fin=heure_fin,
                prix_total=prix_total
            )

            ceo_a_notifier = salle.societer.ceo

            # --- DÉBUT DE LA LOGIQUE DE PAIEMENT CORRIGÉE ---
            if request.user.solde >= prix_total:
                # SOLDE SUFFISANT -> PAIEMENT
                try:
                    with transaction.atomic():
                        # On récupère les objets à jour depuis la BDD
                        client = User.objects.get(pk=request.user.pk)
                        ceo_a_crediter = salle.societer.ceo

                        # Opérations sur les soldes
                        client.solde -= prix_total
                        if ceo_a_crediter:
                            ceo_a_crediter.solde += prix_total
                            ceo_a_crediter.save()
                        
                        client.save()
                        
                        # Mise à jour et sauvegarde de la réservation
                        reservation_instance.etat = 'CONFIRMED'
                        reservation_instance.save()
                
                except Exception as e:
                    messages.error(request, "Une erreur technique est survenue durant le paiement. Veuillez réessayer.")
                    commentaires_salle = Commentaire.objects.filter(reservation__salle=salle)
                    # Pas de redirection ici, on affiche le formulaire à nouveau
                    context = {'salle': salle, 'reservation_form': form,'commentaires': commentaires_salle}
                    return render(request, 'company/salle_detail.html', context)

                # Si la transaction réussit, on envoie les emails
                mail_subject_client = "Votre réservation est confirmée !"
                message_client = render_to_string('reservations/emails/email_reservation_confirmee.html', {'user': request.user, 'reservation': reservation_instance})
                email_client = EmailMessage(mail_subject_client, message_client, to=[request.user.email])
                email_client.content_subtype = "html"
                email_client.send()

                if ceo_a_crediter and ceo_a_crediter.email:
                    mail_subject_ceo = f"Nouvelle réservation pour votre salle {salle.nom}"
                    message_ceo = render_to_string('reservations/emails/email_notif_ceo_nouvelle_resa.html', {'ceo': ceo_a_crediter, 'user': request.user, 'reservation': reservation_instance})
                    email_ceo = EmailMessage(mail_subject_ceo, message_ceo, to=[ceo_a_crediter.email])
                    email_ceo.content_subtype = "html"
                    email_ceo.send()
                
                messages.success(request, f"Réservation confirmée ! Votre solde a été débité de {prix_total}€.")
                return redirect('profile')

            else:
                # SOLDE INSUFFISANT -> EN ATTENTE
                reservation_instance.etat = 'PENDING'
                reservation_instance.save()
                
                # --- CODE D'EMAIL À RÉINTÉGRER ---
                # 1. Email pour le client
                mail_subject_client = "Votre réservation est en attente de paiement"
                message_client = render_to_string('reservations/emails/email_reservation_en_attente.html', {
                    'user': request.user, 
                    'reservation': reservation_instance
                })
                email_client = EmailMessage(mail_subject_client, message_client, to=[request.user.email])
                email_client.content_subtype = "html"
                email_client.send()

                # 2. Email de notification pour le CEO
                if ceo_a_notifier and ceo_a_notifier.email:
                    mail_subject_ceo = f"Nouvelle réservation (en attente) pour votre salle {salle.nom}"
                    message_ceo = render_to_string('reservations/emails/email_notif_ceo_nouvelle_resa.html', {
                        'ceo': ceo_a_notifier, 
                        'user': request.user, 
                        'reservation': reservation_instance
                    })
                    email_ceo = EmailMessage(mail_subject_ceo, message_ceo, to=[ceo_a_notifier.email])
                    email_ceo.content_subtype = "html"
                    email_ceo.send()
                # --- FIN DU CODE D'EMAIL ---

                messages.warning(request, "Votre solde est insuffisant. La réservation est en attente.")

            return redirect('profile')
        else: # Si le formulaire n'est pas valide
            messages.error(request, "Veuillez corriger les erreurs dans le formulaire.")
            # On n'a pas besoin de return ici, le render final s'en occupera
    
    # Si la méthode est GET, ou si le formulaire POST était invalide
    form = ReservationForm(request.POST or None)
    commentaires_salle = Commentaire.objects.filter(reservation__salle=salle)
    context = {'salle': salle, 'reservation_form': form, 'commentaires': commentaires_salle}
    return render(request, 'company/salle_detail.html', context)

class MesReservationsView(LoginRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/mes_reservations.html'
    context_object_name = 'reservations'

    def get_queryset(self):
        return Reservation.objects.filter(user=self.request.user).order_by('-date_reservation', '-heure_debut')
    
    # On ajoute la date actuelle au contexte pour la comparaison dans le template
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        return context

@login_required
def annuler_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user)

    # On ne peut agir que sur une réservation confirmée
    if reservation.etat != 'CONFIRMED':
        messages.error(request, "Seules les réservations confirmées peuvent être annulées.")
        return redirect('reservations:mes_reservations')

    # --- NOUVELLE LOGIQUE DE VERROUILLAGE AUTOMATIQUE ---
    now = timezone.now()
    naive_reservation_datetime = datetime.combine(reservation.date_reservation, reservation.heure_debut)
    aware_reservation_datetime = timezone.make_aware(naive_reservation_datetime)
    
    temps_restant = aware_reservation_datetime - now
    
    # Vérification de la limite des 48 heures
    if temps_restant <= timedelta(hours=48):
        messages.error(request, "Annulation impossible : il reste moins de 48 heures avant le début de votre réservation.")
        return redirect('reservations:mes_reservations')
    
    # --- Si on passe la vérification, l'annulation est autorisée ---
    
    # 1. Annuler la réservation
    reservation.etat = 'CANCELLED'
    reservation.save()

    # 2. Rembourser le CEO
    ceo = reservation.salle.societer.ceo
    if ceo:
        ceo.solde -= reservation.prix_total
        if ceo.solde < 0: ceo.solde = 0
        ceo.save()

    # 3. Générer un code de recharge pour l'utilisateur
    code_remboursement_str = f"REFUND-{uuid.uuid4().hex[:10].upper()}"
    RechargeSolde.objects.create(
        code=code_remboursement_str,
        solde=reservation.prix_total
    )

    # 4. PRÉPARER ET ENVOYER L'EMAIL
    mail_subject = "Confirmation d'annulation et votre code de remboursement"
    message_html = render_to_string('reservations/emails/email_annulation.html', {
        'user': request.user,
        'reservation': reservation,
        'code_remboursement': code_remboursement_str,
    })
    
    email = EmailMessage(
        mail_subject,
        message_html,
        to=[request.user.email] # Envoyer à l'email de l'utilisateur
    )
    email.content_subtype = "html" # Important pour que le HTML soit interprété
    try:
        email.send()
        # Le message de succès est maintenant plus précis
        messages.success(request, f"Votre réservation a été annulée. Un email de confirmation contenant votre code de remboursement de {reservation.prix_total}€ vous a été envoyé.")
    except Exception as e:
        # Gérer le cas où l'email ne part pas
        messages.warning(request, f"Votre réservation a bien été annulée, mais une erreur est survenue lors de l'envoi de l'email de confirmation. Votre code de remboursement est : {code_remboursement_str}")

     # 5. ENVOYER L'EMAIL DE NOTIFICATION AU CEO
    if ceo and ceo.email:
        mail_subject_ceo = f"Annulation de réservation pour la salle {reservation.salle.nom}"
        message_ceo = render_to_string('reservations/emails/email_notif_ceo_annulation.html', {
            'ceo': ceo,
            'user': request.user, # Le client qui a annulé
            'reservation': reservation,
        })
        email_ceo = EmailMessage(mail_subject_ceo, message_ceo, to=[ceo.email])
        email_ceo.content_subtype = "html"
        email_ceo.send() # On peut mettre un try/except ici aussi si on veut

    messages.success(request, f"Votre réservation a été annulée...")
    return redirect('reservations:mes_reservations')


@login_required
def reessayer_paiement(request, pk):
    # On récupère la réservation, en s'assurant qu'elle appartient à l'utilisateur
    # et qu'elle est bien en attente.
    reservation = get_object_or_404(Reservation, pk=pk, user=request.user, etat='PENDING')

    # Vérifier si la réservation n'est pas déjà passée
    now = timezone.now()
    naive_reservation_datetime = datetime.combine(reservation.date_reservation, reservation.heure_debut)
    if timezone.make_aware(naive_reservation_datetime) < now:
        messages.error(request, "Il est trop tard pour payer cette réservation, elle est déjà passée.")
        reservation.etat = 'CANCELLED' # On pourrait l'annuler automatiquement
        reservation.save()
        return redirect('reservations:mes_reservations')

    # Vérification du solde
    if request.user.solde >= reservation.prix_total:
        # PAIEMENT ACCEPTÉ
        
        # 1. Débiter le client
        request.user.solde -= reservation.prix_total
        request.user.save()

        # 2. Créditer le CEO
        ceo = reservation.salle.societer.ceo
        if ceo:
            ceo.solde += reservation.prix_total
            ceo.save()

        # 3. Mettre à jour la réservation
        reservation.etat = 'CONFIRMED'
        reservation.save()
        
        # Envoi de l'email de confirmation au client
        mail_subject = "Votre réservation est maintenant confirmée !"
        message = render_to_string('reservations/emails/email_reservation_confirmee.html', {
            'user': request.user, 'reservation': reservation
        })
        email = EmailMessage(mail_subject, message, to=[request.user.email])
        email.content_subtype = "html"
        email.send()
        
        # (Optionnel) On pourrait aussi renvoyer une notif au CEO pour l'informer du changement de statut

        # ENVOYER L'EMAIL DE NOTIFICATION AU CEO
        ceo = reservation.salle.societer.ceo
        if ceo and ceo.email:
            mail_subject_ceo = f"Paiement reçu pour la réservation de la salle {reservation.salle.nom}"
            message_ceo = render_to_string('reservations/emails/email_notif_ceo_confirmation_paiement.html', {
                'ceo': ceo,
                'user': request.user,
                'reservation': reservation,
            })
            email_ceo = EmailMessage(mail_subject_ceo, message_ceo, to=[ceo.email])
            email_ceo.content_subtype = "html"
            email_ceo.send()

        messages.success(request, f"Paiement réussi ! Votre réservation pour la salle '{reservation.salle.nom}' est maintenant confirmée.")


    
    else:
        # PAIEMENT REFUSÉ
        solde_manquant = reservation.prix_total - request.user.solde
        messages.error(request, f"Votre solde est toujours insuffisant. Il vous manque {solde_manquant}€.")
        
    return redirect('reservations:mes_reservations')

@login_required
def annuler_reservation_admin(request, pk):
    if request.user.role not in ['ADMIN', 'CEO']:
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    # On récupère la réservation sans vérifier le propriétaire, car un admin peut voir plusieurs sociétés
    # La sécurité se fera sur le droit d'accès à la page de gestion.
    reservation = get_object_or_404(Reservation, pk=pk)

    # On ne peut annuler que ce qui n'est pas déjà annulé ou terminé
    if reservation.etat in ['CANCELLED', 'COMPLETED']:
        messages.warning(request, "Cette réservation est déjà terminée ou annulée.")
        return redirect('reservations:gestion_reservations')

    client_a_rembourser = reservation.user
    ceo_a_debiter = reservation.salle.societer.ceo
    montant = reservation.prix_total

    try:
        with transaction.atomic():
            # On met à jour l'état de la réservation
            reservation.etat = 'CANCELLED'
            reservation.save()

            # --- MISE À JOUR SÉCURISÉE DES SOLDES ---
            # 1. Rembourser le client (crédit direct sur le solde)
            client_a_rembourser.solde += montant
            client_a_rembourser.save()

            # 2. Débiter le CEO
            if ceo_a_debiter:
                ceo_a_debiter.solde -= montant
                ceo_a_debiter.save()
    
    except Exception as e:
        messages.error(request, f"Une erreur technique est survenue : {e}")
        return redirect('reservations:gestion_reservations')

    # --- ENVOI DE L'EMAIL DE NOTIFICATION AU CLIENT ---
    mail_subject = f"Annulation de votre réservation pour la salle {reservation.salle.nom}"
    message_html = render_to_string('reservations/emails/email_client_annulation_par_admin.html', {
        'user': client_a_rembourser,
        'reservation': reservation,
    })
    email = EmailMessage(mail_subject, message_html, to=[client_a_rembourser.email])
    email.content_subtype = "html"
    email.send()

    messages.success(request, f"La réservation de {client_a_rembourser.username} a été annulée. Le client a été remboursé et notifié par email.")
    return redirect('gestion_reservations')

class GestionReservationsView(AdminRoleRequiredMixin, ListView):
    model = Reservation
    template_name = 'reservations/gestion_reservations_list.html'
    context_object_name = 'reservations'
    paginate_by = 20 # Afficher 20 réservations par page

    def get_queryset(self):
        user = self.request.user
        queryset = Reservation.objects.all()

        # --- Filtrage initial par société ---
        if user.role == 'CEO':
            queryset = queryset.filter(salle__societer__ceo=user)
        elif user.role == 'ADMIN':
            # On suppose qu'un admin est lié à une société
            # (logique à ajouter plus tard, pour l'instant on fait comme pour le CEO)
            # Idéalement, on aurait un champ "societe" sur le modèle User de l'admin
            try:
                societe_admin = user.societe_ceo # Placeholder, on assumera qu'un admin est lié au CEO pour l'instant
                queryset = queryset.filter(salle__societer=societe_admin)
            except:
                # Si l'admin n'est pas lié, il ne voit rien
                return Reservation.objects.none()

        # --- Filtrage par les paramètres GET ---
        salle_id = self.request.GET.get('salle')
        etat = self.request.GET.get('etat')
        date = self.request.GET.get('date')

        if salle_id:
            queryset = queryset.filter(salle_id=salle_id)
        if etat:
            queryset = queryset.filter(etat=etat)
        if date:
            queryset = queryset.filter(date_reservation=date)

        return queryset.order_by('-date_reservation', '-heure_debut')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # On passe les salles de la société pour le filtre déroulant
        if self.request.user.role == 'CEO':
            context['salles_filtre'] = Salle.objects.filter(societer__ceo=self.request.user)
        # Ajouter la logique pour l'admin si nécessaire
        
        return context
    

@login_required
def laisser_commentaire_view(request, reservation_id):
    reservation = get_object_or_404(Reservation, pk=reservation_id, user=request.user)

    # Sécurités : On ne peut commenter qu'une réservation terminée et non déjà commentée
    if reservation.etat != 'COMPLETED':
        messages.error(request, "Vous ne pouvez laisser un avis que pour une réservation terminée.")
        return redirect('reservations:mes_reservations')
    if hasattr(reservation, 'commentaire'):
        messages.error(request, "Vous avez déjà laissé un avis pour cette réservation.")
        return redirect('reservations:mes_reservations')

    if request.method == 'POST':
        form = CommentaireForm(request.POST)
        if form.is_valid():
            commentaire = form.save(commit=False)
            commentaire.reservation = reservation
            commentaire.save()

            # --- MISE À JOUR DES NOTES MOYENNES ---
            salle = reservation.salle
            
            # Mettre à jour la note de la salle
            nouvelle_note_salle = Commentaire.objects.filter(reservation__salle=salle).aggregate(moyenne=Avg('note'))['moyenne']
            salle.vote = round(nouvelle_note_salle, 2)
            salle.save()
            
            # Mettre à jour la note de la société
            societe = salle.societer
            note_moyenne_societe = societe.salles.all().aggregate(moyenne=Avg('vote'))['moyenne']
            societe.vote = round(note_moyenne_societe, 2)
            societe.save()

            messages.success(request, "Merci ! Votre avis a bien été enregistré.")
            return redirect('reservations:mes_reservations')
    else:
        form = CommentaireForm()

    context = {
        'form': form,
        'reservation': reservation
    }
    return render(request, 'reservations/laisser_commentaire.html', context)