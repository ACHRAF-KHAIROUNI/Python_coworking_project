# users/urls.py
from django.urls import path
# On importe les vues d'authentification de Django
from django.contrib.auth import views as auth_views 
from . import views

urlpatterns = [
    # URLs d'inscription et d'activation (déjà existantes)
    path('register/', views.register_view, name='register'),
    path('activate/<uidb64>/<token>/', views.activate_view, name='activate'),

    # URLs d'authentification
    path('login/', views.custom_login_view, name='login'),
    path('logout/', views.custom_logout_view, name='logout'),
    # URL du profil utilisateur
    path('profile/', views.profile_view, name='profile'),
    
]