# users/views.py

from django.shortcuts import render, redirect
from django.contrib.sites.shortcuts import get_current_site
from django.template.loader import render_to_string
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.tokens import default_token_generator
from django.contrib.auth.decorators import login_required

from reservations.models import Reservation
from users.mixins import AdminRoleRequiredMixin

from .forms import UserRegisterForm
from .models import User

from django.contrib.auth import authenticate, login, logout 
from .forms import UserRegisterForm, UserLoginForm 



from django.utils import timezone 
from django.contrib import messages 

# Importer le formulaire et le modèle de l'application finances
from finances.forms import RechargeForm
from finances.models import RechargeSolde

from django.views.generic import ListView

def register_view(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            # Ne sauvegarde pas encore l'utilisateur dans la base de données
            user = form.save(commit=False)
            user.is_active = False # Django utilise is_active, nous l'alignons sur notre champ 'etat'
            user.etat = False
            user.set_password(form.cleaned_data['password']) # Hacher le mot de passe
            user.save()

            # Logique d'envoi d'email
            current_site = get_current_site(request)
            mail_subject = 'Activez votre compte Coworking.'
            
            # Le message est rendu à partir d'un template pour être plus propre
            message = render_to_string('users/emails/activation_email.html', {
                'user': user,
                'domain': current_site.domain,
                'uid': urlsafe_base64_encode(force_bytes(user.pk)),
                'token': default_token_generator.make_token(user),
            })
            
            
            to_email = form.cleaned_data.get('email')
            email = EmailMessage(
                mail_subject, message, to=[to_email]
            )
            email.send(fail_silently=False)

            # Rediriger vers une page indiquant de vérifier les emails
            return render(request, 'users/registration_pending.html')
    else:
        form = UserRegisterForm()
        
    return render(request, 'users/register.html', {'form': form})

# Nous ajouterons la vue d'activation ici plus tard

from django.http import HttpResponse # Assurez-vous d'importer HttpResponse en haut

def activate_view(request, uidb64, token):
    try:
        # On décode l'uid pour retrouver la clé primaire (pk) de l'utilisateur
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    # On vérifie que l'utilisateur existe ET que le token est valide
    if user is not None and default_token_generator.check_token(user, token):
        # On active l'utilisateur
        user.is_active = True
        user.etat = True
        user.save()
        
        # Affichez un message de succès
        # Plus tard, on pourra utiliser le framework de messages de Django
        return render(request, 'users/activation_complete.html')
    else:
        # Le lien est invalide
        return render(request, 'users/activation_invalid.html')


@login_required
def profile_view(request):
    user = request.user
    recharge_form = RechargeForm() # Initialiser le formulaire vide

    if request.method == 'POST':
        # On ne traite que le formulaire de recharge pour l'instant
        form = RechargeForm(request.POST)
        if form.is_valid():
            code_saisi = form.cleaned_data['code']
            try:
                # 1. Vérifier si le code existe et est disponible
                recharge_code = RechargeSolde.objects.get(code=code_saisi, etat_consommation__isnull=True)
                
                # 2. Mettre à jour le solde de l'utilisateur
                user.solde += recharge_code.solde
                user.save()
                
                # 3. Marquer le code comme utilisé
                recharge_code.etat_consommation = user
                recharge_code.date_consommation = timezone.now()
                recharge_code.save()
                # --- Envoi de l'email de confirmation de recharge ---
                mail_subject = "Votre compte a été rechargé"
                message = render_to_string('finances/emails/email_recharge.html', {
                    'user': user,
                    'montant_recharge': recharge_code.solde,
                    'code': recharge_code.code,
                    'nouveau_solde': user.solde
                })
                email = EmailMessage(mail_subject, message, to=[user.email])
                email.content_subtype = "html"
                email.send()

                messages.success(request, f"Votre compte a été rechargé de {recharge_code.solde}€. Votre nouveau solde est de {user.solde}€.")
            except RechargeSolde.DoesNotExist:
                # Le code n'existe pas ou a déjà été utilisé
                messages.error(request, "Le code de recharge est invalide ou a déjà été utilisé.")
        
        # Rediriger vers la même page pour afficher le message et rafraîchir les données
        return redirect('profile')

    # Si la méthode est GET, on affiche simplement la page
    # On passe le formulaire vide au template
    return render(request, 'users/profile.html', {
        'user': user,
        'recharge_form': recharge_form
    })



def custom_login_view(request):
    form = UserLoginForm(request.POST or None)
    if request.method == 'POST' and form.is_valid():
        username = form.cleaned_data.get('username')
        password = form.cleaned_data.get('password')
        
        # On authentifie l'utilisateur
        user = authenticate(request, username=username, password=password)

        if user is not None:
            # L'utilisateur existe et le mot de passe est correct
            
            # --- NOTRE VÉRIFICATION PERSONNALISÉE ---
            if user.etat: # 'etat' est notre champ pour l'activation par email
                login(request, user)
                return redirect('profile') # Rediriger vers le profil après connexion
            else:
                # Le compte n'est pas activé
                messages.error(request, "Votre compte n'a pas encore été activé. Veuillez vérifier vos emails pour le lien d'activation.")
        else:
            # L'authentification a échoué (mauvais username/password)
            messages.error(request, "Nom d'utilisateur ou mot de passe incorrect.")
    
    return render(request, 'users/login.html', {'form': form})

# On doit aussi créer une vue pour la déconnexion si on n'utilise plus celles de Django
def custom_logout_view(request):
    logout(request)
    messages.info(request, "Vous avez été déconnecté.")
    return redirect('login')


