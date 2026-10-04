# company/forms.py
from django import forms
from .models import Salle, ImageSalle,Materiel, SalleMateriel

# company/forms.py
from django import forms
from .models import Salle

class SalleForm(forms.ModelForm):
    class Meta:
        model = Salle
        fields = [
            'nom', 'capacite', 'description', 'prix_par_heure', 
            'latitude', 'longitude', 'heurD', 'heurF'
        ]
        # ON SUPPRIME TOUTE LA SECTION 'widgets' ET 'labels'

class ImageSalleForm(forms.ModelForm):
    # Champ de fichier non lié au modèle
    image_file = forms.FileField(label="Image", required=True)

    class Meta:
        model = ImageSalle
        fields = ['legende']  # On ne met PAS 'image' ici

class ReservationForm(forms.Form):
    date_reservation = forms.DateField(
        label="Date",
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    heure_debut = forms.TimeField(
        label="Heure de début",
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    duree_heures = forms.IntegerField(
        label="Durée (en heures)",
        min_value=1, # Durée minimale de 1 heure
        initial=1
    )


class MaterielForm(forms.ModelForm):
    class Meta:
        model = Materiel
        fields = ['nom', 'description', 'categorie']

class SalleMaterielForm(forms.ModelForm):
    class Meta:
        model = SalleMateriel
        fields = ['materiel', 'quantite']

    def __init__(self, *args, **kwargs):
        # On ne veut pas lier le formulaire à une société ici,
        # car le matériel est global pour l'instant
        super().__init__(*args, **kwargs)
        self.fields['materiel'].queryset = Materiel.objects.all().order_by('nom')