from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import Utilisateur

@admin.register(Utilisateur)
class UtilisateurAdmin(UserAdmin):
    list_display = ['username', 'email', 'first_name', 'last_name', 'role', 'est_verifie']
    list_filter = ['role', 'est_verifie']
    fieldsets = UserAdmin.fieldsets + (
        ('Infos AkwabaFoncier', {'fields': ('role', 'telephone', 'adresse', 'piece_identite', 'numero_piece', 'photo', 'est_verifie')}),
    )
