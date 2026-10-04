# company/urls.py
from django.urls import path
from . import views
from . import views as company_views # On donne un alias pour éviter les conflits
from reservations import views as reservation_views # On importe les vues de l'app
from reservations.views import salle_detail_and_reservation_view 

app_name = 'company' # Important pour nommer les URLs

urlpatterns = [
    # URLs de gestion pour le CEO
    path('dashboard/', views.DashboardView.as_view(), name='dashboard'),
    path('salle/ajouter/', views.SalleCreateView.as_view(), name='salle_add'),
    path('salle/<int:pk>/modifier/', views.SalleUpdateView.as_view(), name='salle_update'),
    path('salle/<int:pk>/supprimer/', views.SalleDeleteView.as_view(), name='salle_delete'),
    path('salle/<int:pk>/gerer/', views.SalleManageView.as_view(), name='salle_manage'), 
    path('salle/<int:pk>/add-image/', views.add_image_to_salle, name='salle_add_image'), 
    path('image/<int:pk>/delete/', views.delete_image_from_salle, name='salle_delete_image'), 

    # URLs publiques
    path('salles/', views.SalleListView.as_view(), name='salle_list'),
    #path('salles/<int:pk>/', views.SalleDetailView.as_view(), name='salle_detail'),
    
    # URL de réservation (utilise reservation_views)
    #path('salles/<int:pk>/reserver/', reservation_views.create_reservation, name='create_reservation'),
    path('salles/<int:pk>/', salle_detail_and_reservation_view, name='salle_detail'),
    
    path('admins/', views.GestionAdminsView.as_view(), name='gestion_admins'),
    path('admins/nommer/', views.nommer_admin, name='nommer_admin'),
    path('admins/revoquer/<int:user_id>/', views.revoquer_admin, name='revoquer_admin'),

    path('materiel/', views.GestionMaterielView.as_view(), name='gestion_materiel'),
    path('materiel/ajouter/', views.ajouter_materiel, name='ajouter_materiel'),
    path('materiel/<int:pk>/supprimer/', views.supprimer_materiel, name='supprimer_materiel'),

    path('salle/<int:pk>/assigner-materiel/', views.assigner_materiel_salle, name='assigner_materiel_salle'),
    path('salle-materiel/<int:pk>/retirer/', views.retirer_materiel_salle, name='retirer_materiel_salle'),

    
]