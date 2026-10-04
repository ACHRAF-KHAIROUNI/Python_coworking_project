# finances/forms.py
from django import forms

class RechargeForm(forms.Form):
    code = forms.CharField(
        label="Code de recharge",
        max_length=50,
        widget=forms.TextInput(attrs={'placeholder': 'Entrez votre code ici'})
    )