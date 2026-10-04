# users/mixins.py
from django.contrib.auth.mixins import AccessMixin
from django.shortcuts import redirect

class CEORoleRequiredMixin(AccessMixin):
    """
    Vérifie que l'utilisateur connecté a le rôle 'CEO'.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role != 'CEO':
            # Rediriger vers le profil si l'utilisateur n'est pas un CEO
            # On pourrait aussi afficher une page 403 Forbidden
            return redirect('profile') 
        return super().dispatch(request, *args, **kwargs)

class AdminRoleRequiredMixin(AccessMixin):
    """
    Vérifie que l'utilisateur connecté a le rôle 'ADMIN' ou 'CEO'.
    Un CEO a les droits d'un Admin.
    """
    def dispatch(self, request, *args, **kwargs):
        if not request.user.is_authenticated:
            return self.handle_no_permission()
        if request.user.role not in ['ADMIN', 'CEO']:
            return redirect('profile')
        return super().dispatch(request, *args, **kwargs)