# reservations/forms.py
from django import forms
from .models import Reservation, Commentaire

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

class CommentaireForm(forms.ModelForm):
    class Meta:
        model = Commentaire
        # On ne demande que la note et le texte, la réservation sera liée dans la vue.
        fields = ['note', 'texte']
        widgets = {
            'note': forms.NumberInput(attrs={'type': 'number', 'min': 1, 'max': 5}),
            'texte': forms.Textarea(attrs={'rows': 4, 'placeholder': 'Votre commentaire...'}),
        }
        labels = {
            'note': 'Votre note (de 1 à 5)',
            'texte': 'Votre avis',
        }