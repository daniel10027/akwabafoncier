from django.contrib import admin
from .models import Commune, Quartier, Terrain, DocumentFoncier, HistoriqueTerrain, DemandeProcedure, Reclamation, Alerte

admin.site.register(Commune)
admin.site.register(Quartier)

@admin.register(Terrain)
class TerrainAdmin(admin.ModelAdmin):
    list_display = ['reference_cadastrale', 'commune', 'statut', 'superficie', 'proprietaire_actuel', 'alerte_active']
    list_filter = ['statut', 'commune', 'zone_usage', 'alerte_active']
    search_fields = ['reference_cadastrale', 'adresse_complete']

admin.site.register(DocumentFoncier)
admin.site.register(HistoriqueTerrain)
admin.site.register(DemandeProcedure)
admin.site.register(Reclamation)
admin.site.register(Alerte)
