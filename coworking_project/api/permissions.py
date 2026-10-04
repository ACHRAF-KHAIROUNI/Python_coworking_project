# api/permissions.py
from rest_framework import permissions
from company.models import Administrateur

class IsAdminOfAssociatedCompany(permissions.BasePermission):
    """
    Permission pour vérifier si l'utilisateur est un admin
    et agit sur une ressource de sa propre société.
    """
    def has_permission(self, request, view):
        # L'utilisateur doit avoir le rôle ADMIN
        if not request.user.is_authenticated or request.user.role != 'ADMIN':
            return False
        
        # L'utilisateur doit être lié à une société via la table Administrateur
        try:
            Administrateur.objects.get(user=request.user)
            return True
        except Administrateur.DoesNotExist:
            return False