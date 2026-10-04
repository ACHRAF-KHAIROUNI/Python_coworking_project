# company/admin.py
from django.contrib import admin
from .models import Administrateur, Societer, Salle, Materiel, SalleMateriel, ImageSalle

admin.site.register(Societer)
admin.site.register(Salle)
admin.site.register(Materiel)
admin.site.register(SalleMateriel)
admin.site.register(ImageSalle)
admin.site.register(Administrateur)