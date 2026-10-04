# company/views.py
from sqlite3 import IntegrityError
from django.shortcuts import get_object_or_404, redirect, render
from django.views.generic import TemplateView, CreateView
from django.urls import reverse_lazy

from users.mixins import CEORoleRequiredMixin 
from .models import ImageSalle, Salle, SalleMateriel, Societer

from .forms import SalleForm, ImageSalleForm, SalleMaterielForm
from django.contrib import messages
from django.views.generic import ListView, DetailView
from django.views.generic import (
    TemplateView, CreateView, UpdateView, DeleteView 
)

from users.models import User
from .models import Administrateur, Societer
from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required

from reservations.forms import ReservationForm
from django.views.generic import ListView

from django.core.mail import EmailMessage
from django.template.loader import render_to_string

from .models import Materiel
from .forms import MaterielForm


class DashboardView(CEORoleRequiredMixin, TemplateView):
    template_name = 'company/dashboard.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user = self.request.user
        try:
            # Récupérer la société gérée par le CEO connecté
            societe = Societer.objects.get(ceo=user)
            context['societe'] = societe
            # Récupérer les salles de cette société
            context['salles'] = Salle.objects.filter(societer=societe)
        except Societer.DoesNotExist:
            context['societe'] = None
            context['salles'] = []
        
        return context

class SalleCreateView(CEORoleRequiredMixin, CreateView):
    model = Salle
    form_class = SalleForm
    template_name = 'company/salle_form.html'
    success_url = reverse_lazy('company:dashboard') # Rediriger vers le dashboard après succès

    def form_valid(self, form):
        # Cette méthode est appelée quand le formulaire est valide
        salle = form.save(commit=False) # Ne pas sauvegarder tout de suite

        # Associer la salle à la société du CEO connecté
        try:
            societe_ceo = Societer.objects.get(ceo=self.request.user)
            salle.societer = societe_ceo
            salle.save() # Maintenant on peut sauvegarder
        except Societer.DoesNotExist:
            # Gérer le cas (peu probable) où le CEO n'a pas de société
            form.add_error(None, "Erreur : Impossible de trouver votre société.")
            return self.form_invalid(form)

        messages.success(self.request, f"La salle '{salle.nom}' a été créée avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        # Ajouter des informations au contexte si nécessaire
        context = super().get_context_data(**kwargs)
        context['titre_page'] = "Ajouter une nouvelle salle"
        return context
    
class SalleListView(ListView):
    model = Salle
    template_name = 'company/salle_list.html'
    context_object_name = 'salles' # Nom de la variable dans le template

    def get_queryset(self):
        # On ne montre que les salles des sociétés actives
        return Salle.objects.filter(societer__etat='ACTIVE').order_by('nom')

class SalleDetailView(DetailView):
    model = Salle
    template_name = 'company/salle_detail.html'
    context_object_name = 'salle' # Nom de la variable dans le template

    def get_queryset(self):
        # Sécurité : on s'assure qu'on ne peut voir que les salles des sociétés actives
        return Salle.objects.filter(societer__etat='ACTIVE')
    

class SalleUpdateView(CEORoleRequiredMixin, UpdateView):
    model = Salle
    form_class = SalleForm
    template_name = 'company/salle_form.html'
    success_url = reverse_lazy('company:dashboard')

    def get_queryset(self):
        # Sécurité : Le CEO ne peut modifier que les salles de sa propre société
        return Salle.objects.filter(societer__ceo=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, f"La salle '{form.instance.nom}' a été modifiée avec succès.")
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['titre_page'] = "Modifier la salle"
        return context

class SalleDeleteView(CEORoleRequiredMixin, DeleteView):
    model = Salle
    template_name = 'company/salle_confirm_delete.html'
    success_url = reverse_lazy('company:dashboard')

    def get_queryset(self):
        # Sécurité : Le CEO ne peut supprimer que les salles de sa propre société
        return Salle.objects.filter(societer__ceo=self.request.user)

    def form_valid(self, form):
        # On ajoute un message de succès avant de supprimer
        messages.success(self.request, f"La salle '{self.object.nom}' a été supprimée avec succès.")
        return super().form_valid(form)

def home_view(request):
    return redirect('company:salle_list')

class SalleManageView(CEORoleRequiredMixin, DetailView):
    model = Salle
    template_name = 'company/salle_manage.html'
    context_object_name = 'salle'

    def get_queryset(self):
        # Sécurité : le CEO ne peut gérer que ses propres salles
        return Salle.objects.filter(societer__ceo=self.request.user)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['image_form'] = ImageSalleForm()
        context['materiel_form'] = SalleMaterielForm()
        return context

from cloudinary.uploader import upload
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .forms import ImageSalleForm
from .models import Salle, ImageSalle

def add_image_to_salle(request, pk):
    salle = get_object_or_404(Salle, pk=pk, societer__ceo=request.user)

    if request.method == 'POST':
        form = ImageSalleForm(request.POST, request.FILES)
        if form.is_valid():
            image_file = request.FILES['image_file']
            result = upload(image_file, folder="COWORKING_PROJECT/salles_images/")  # optionnel mais propre
            url = result['secure_url']

            image_instance = form.save(commit=False)
            image_instance.salle = salle
            image_instance.image = url
            image_instance.save()

            messages.success(request, "L'image a été ajoutée avec succès.")
            return redirect('company:salle_manage', pk=salle.pk)
    else:
        form = ImageSalleForm()

    return render(request, 'company/add_image.html', {'form': form, 'salle': salle})



def delete_image_from_salle(request, pk):
    image = get_object_or_404(ImageSalle, pk=pk, salle__societer__ceo=request.user)
    salle_pk = image.salle.pk
    image.delete()
    messages.success(request, "L'image a été supprimée.")
    return redirect('company:salle_manage', pk=salle_pk)

class GestionAdminsView(CEORoleRequiredMixin, View):
    template_name = 'company/gestion_admins.html'

    def get(self, request, *args, **kwargs):
        # Récupérer la société du CEO connecté
        societe_ceo = get_object_or_404(Societer, ceo=request.user)
        
        # Récupérer les objets Administrateur liés à cette société
        admins_obj = Administrateur.objects.filter(societe=societe_ceo)
        
        context = {
            'admins': admins_obj
        }
        return render(request, self.template_name, context)

@login_required
def nommer_admin(request):
    if request.user.role != 'CEO':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    if request.method == 'POST':
        username = request.POST.get('username')
        societe_ceo = get_object_or_404(Societer, ceo=request.user)
        
        try:
            user_a_promouvoir = User.objects.get(username=username)

            # Vérifications de sécurité
            if user_a_promouvoir.role != 'USER':
                messages.error(request, f"L'utilisateur {username} n'est pas un client simple. Il ne peut pas être promu.")
            elif Administrateur.objects.filter(user=user_a_promouvoir).exists():
                messages.error(request, f"L'utilisateur {username} est déjà un administrateur.")
            else:
                # Promotion de l'utilisateur
                user_a_promouvoir.role = 'ADMIN'
                user_a_promouvoir.save()

                # Création de l'entrée dans la table Administrateur
                Administrateur.objects.create(user=user_a_promouvoir, societe=societe_ceo)

                # --- ENVOI DE L'EMAIL DE PROMOTION ---
                mail_subject = "Vous avez été promu Administrateur"
                message = render_to_string('company/emails/email_promotion_admin.html', {
                    'user_promu': user_a_promouvoir,
                    'societe': societe_ceo,
                    'ceo': request.user
                })
                email = EmailMessage(mail_subject, message, to=[user_a_promouvoir.email])
                email.content_subtype = "html"
                email.send()

                messages.success(request, f"L'utilisateur {username} a été promu Administrateur de votre société.")
        
        except User.DoesNotExist:
            messages.error(request, f"Aucun utilisateur trouvé avec le nom d'utilisateur '{username}'.")
            
    return redirect('company:gestion_admins')


@login_required
def revoquer_admin(request, user_id):
    if request.user.role != 'CEO':
        messages.error(request, "Accès non autorisé.")
        return redirect('home')

    societe_ceo = get_object_or_404(Societer, ceo=request.user)
    user_a_revoquer = get_object_or_404(User, pk=user_id)

    # On cherche l'entrée admin correspondante
    admin_obj = get_object_or_404(Administrateur, user=user_a_revoquer, societe=societe_ceo)

    # Révocation
    user_a_revoquer.role = 'USER'
    user_a_revoquer.save()
    admin_obj.delete() # On supprime la liaison

    # --- ENVOI DE L'EMAIL DE RÉVOCATION ---
    mail_subject = "Fin de vos fonctions d'Administrateur"
    message = render_to_string('company/emails/email_revocation_admin.html', {
        'user_revoque': user_a_revoquer,
        'societe': societe_ceo,
    })
    email = EmailMessage(mail_subject, message, to=[user_a_revoquer.email])
    email.content_subtype = "html"
    email.send()

    messages.success(request, f"L'utilisateur {user_a_revoquer.username} n'est plus administrateur.")
    return redirect('company:gestion_admins')


class GestionMaterielView(CEORoleRequiredMixin, ListView):
    model = Materiel
    template_name = 'company/gestion_materiel.html'
    context_object_name = 'materiels'

    def get_queryset(self):
        # Pour l'instant, on suppose que le matériel est global, 
        # mais on pourrait le lier à une société plus tard.
        # Pour l'instant, on liste tout.
        return Materiel.objects.all().order_by('nom')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = MaterielForm()
        return context

def ajouter_materiel(request):
    if request.method == 'POST' and request.user.role == 'CEO':
        form = MaterielForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Le matériel a été ajouté à la liste générale.")
        else:
            messages.error(request, "Erreur dans le formulaire.")
    return redirect('company:gestion_materiel')

def supprimer_materiel(request, pk):
    if request.user.role == 'CEO':
        materiel = get_object_or_404(Materiel, pk=pk)
        materiel.delete()
        messages.success(request, f"Le matériel '{materiel.nom}' a été supprimé de la liste générale.")
    return redirect('company:gestion_materiel')


def assigner_materiel_salle(request, pk):
    if request.method == 'POST' and request.user.role == 'CEO':
        salle = get_object_or_404(Salle, pk=pk, societer__ceo=request.user)
        form = SalleMaterielForm(request.POST)
        if form.is_valid():
            materiel_selectionne = form.cleaned_data.get('materiel')
            quantite_soumise = form.cleaned_data.get('quantite')
            salle_materiel_obj, created = SalleMateriel.objects.get_or_create(
                salle=salle,
                materiel=materiel_selectionne,
                # defaults est utilisé seulement si l'objet est créé
                defaults={'quantite': quantite_soumise} 
            )

            if not created:
                # L'objet existait déjà, donc on met juste à jour la quantité.
                salle_materiel_obj.quantite = quantite_soumise
                salle_materiel_obj.save()
                messages.success(request, f"La quantité pour '{materiel_selectionne.nom}' a été mise à jour.")
            else:
                # L'objet a été créé avec succès.
                messages.success(request, f"Le matériel '{materiel_selectionne.nom}' a été assigné à la salle.")

        else:
            messages.error(request, "Formulaire invalide.")
            
    return redirect('company:salle_manage', pk=pk)

# Ajouter aussi une vue pour supprimer le matériel d'une salle
def retirer_materiel_salle(request, pk):
    # pk est ici l'id de l'objet SalleMateriel
    if request.user.role == 'CEO':
        salle_materiel = get_object_or_404(SalleMateriel, pk=pk, salle__societer__ceo=request.user)
        salle_pk = salle_materiel.salle.pk
        salle_materiel.delete()
        messages.success(request, "Le matériel a été retiré de la salle.")
        return redirect('company:salle_manage', pk=salle_pk)
    return redirect('home')