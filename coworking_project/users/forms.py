# users/forms.py

from django import forms
from .models import User

class UserRegisterForm(forms.ModelForm):
    # On ajoute des champs pour le mot de passe pour avoir la confirmation
    password = forms.CharField(widget=forms.PasswordInput)
    password2 = forms.CharField(label='Confirm password', widget=forms.PasswordInput)

    class Meta:
        model = User
        # Les champs que l'utilisateur devra remplir
        fields = ['username', 'first_name', 'last_name', 'email']

    def clean_password2(self):
        # Méthode spéciale pour valider un champ spécifique
        cd = self.cleaned_data
        if cd['password'] != cd['password2']:
            raise forms.ValidationError('Les mots de passe ne correspondent pas.')
        return cd['password2']

    def clean_email(self):
        # Méthode pour s'assurer que l'email n'est pas déjà utilisé
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("Un compte avec cet email existe déjà.")
        return email
    
class UserLoginForm(forms.Form):
    username = forms.CharField(label="Nom d'utilisateur")
    password = forms.CharField(widget=forms.PasswordInput, label="Mot de passe")