from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.db.models import Q, Count
from django.views.decorators.csrf import csrf_exempt
import json
from .models import Terrain, Commune, Quartier, DocumentFoncier, HistoriqueTerrain, DemandeProcedure, Reclamation, Alerte
from utilisateurs.models import Utilisateur

def is_admin(user):
    return user.is_authenticated and user.role in ['admin_operationnel', 'super_admin']

@login_required
def dashboard(request):
    user = request.user
    if user.role in ['admin_operationnel', 'super_admin']:
        return redirect('admin_dashboard')
    terrains = Terrain.objects.filter(proprietaire_actuel=user)[:5]
    demandes = DemandeProcedure.objects.filter(demandeur=user).order_by('-date_soumission')[:5]
    reclamations = Reclamation.objects.filter(plaignant=user).order_by('-date_depot')[:5]
    return render(request, 'foncier/dashboard.html', {
        'terrains': terrains, 'demandes': demandes, 'reclamations': reclamations
    })

@login_required
def liste_terrains(request):
    q = request.GET.get('q', '')
    commune = request.GET.get('commune', '')
    statut = request.GET.get('statut', '')
    terrains = Terrain.objects.all()
    if q:
        terrains = terrains.filter(Q(reference_cadastrale__icontains=q) | Q(adresse_complete__icontains=q))
    if commune:
        terrains = terrains.filter(commune__id=commune)
    if statut:
        terrains = terrains.filter(statut=statut)
    communes = Commune.objects.all()
    return render(request, 'foncier/liste_terrains.html', {
        'terrains': terrains, 'communes': communes, 'statut_choices': Terrain.STATUT_CHOICES
    })

@login_required
def detail_terrain(request, pk):
    terrain = get_object_or_404(Terrain, pk=pk)
    historique = terrain.historique.all()[:10]
    documents = terrain.documents.all()
    alertes = terrain.alertes.filter(est_active=True)
    return render(request, 'foncier/detail_terrain.html', {
        'terrain': terrain, 'historique': historique, 'documents': documents, 'alertes': alertes
    })

@login_required
def verification_terrain(request):
    terrain = None
    if request.method == 'POST':
        ref = request.POST.get('reference', '').strip().upper()
        if ref:
            terrain = Terrain.objects.filter(reference_cadastrale__iexact=ref).first()
    return render(request, 'foncier/verification.html', {'terrain': terrain})

@login_required
def mes_demandes(request):
    demandes = DemandeProcedure.objects.filter(demandeur=request.user).order_by('-date_soumission')
    return render(request, 'foncier/mes_demandes.html', {'demandes': demandes})

@login_required
def nouvelle_demande(request):
    terrains = Terrain.objects.all()
    if request.method == 'POST':
        terrain_id = request.POST.get('terrain')
        terrain = get_object_or_404(Terrain, pk=terrain_id)
        demande = DemandeProcedure.objects.create(
            type_demande=request.POST.get('type_demande'),
            terrain=terrain,
            demandeur=request.user,
            description=request.POST.get('description', ''),
        )
        HistoriqueTerrain.objects.create(
            terrain=terrain,
            action=f"Nouvelle demande {demande.type_demande}",
            description=f"Demande {demande.reference} soumise",
            effectue_par=request.user,
        )
        messages.success(request, f'Demande {demande.reference} soumise avec succès !')
        return redirect('mes_demandes')
    return render(request, 'foncier/nouvelle_demande.html', {
        'terrains': terrains,
        'type_choices': DemandeProcedure.TYPE_CHOICES
    })

@login_required
def detail_demande(request, pk):
    demande = get_object_or_404(DemandeProcedure, pk=pk, demandeur=request.user)
    return render(request, 'foncier/detail_demande.html', {'demande': demande})

@login_required
def mes_reclamations(request):
    reclamations = Reclamation.objects.filter(plaignant=request.user).order_by('-date_depot')
    return render(request, 'foncier/mes_reclamations.html', {'reclamations': reclamations})

@login_required
def nouvelle_reclamation(request):
    terrains = Terrain.objects.all()
    if request.method == 'POST':
        terrain = get_object_or_404(Terrain, pk=request.POST.get('terrain'))
        reclamation = Reclamation.objects.create(
            terrain=terrain,
            plaignant=request.user,
            objet=request.POST.get('objet', ''),
            description_detaillee=request.POST.get('description', ''),
        )
        terrain.alerte_active = True
        terrain.save()
        messages.success(request, f'Réclamation {reclamation.reference} déposée !')
        return redirect('mes_reclamations')
    return render(request, 'foncier/nouvelle_reclamation.html', {'terrains': terrains})

# ===== ADMIN VIEWS =====
@login_required
def admin_dashboard(request):
    if not is_admin(request.user):
        messages.error(request, 'Accès refusé.')
        return redirect('dashboard')
    stats = {
        'total_terrains': Terrain.objects.count(),
        'terrains_litige': Terrain.objects.filter(statut='litige').count(),
        'demandes_en_cours': DemandeProcedure.objects.filter(statut__in=['soumise', 'en_cours']).count(),
        'reclamations_actives': Reclamation.objects.filter(statut__in=['deposee', 'en_analyse']).count(),
        'alertes_actives': Alerte.objects.filter(est_active=True).count(),
        'utilisateurs': Utilisateur.objects.count(),
        'terrains_par_statut': list(Terrain.objects.values('statut').annotate(count=Count('id'))),
        'demandes_recentes': DemandeProcedure.objects.order_by('-date_soumission')[:10],
        'alertes_recentes': Alerte.objects.filter(est_active=True).order_by('-date_creation')[:5],
    }
    return render(request, 'foncier/admin/dashboard.html', {'stats': stats})

@login_required
def admin_terrains(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    q = request.GET.get('q', '')
    statut = request.GET.get('statut', '')
    terrains = Terrain.objects.select_related('commune', 'proprietaire_actuel').all()
    if q:
        terrains = terrains.filter(Q(reference_cadastrale__icontains=q) | Q(adresse_complete__icontains=q))
    if statut:
        terrains = terrains.filter(statut=statut)
    return render(request, 'foncier/admin/terrains.html', {
        'terrains': terrains, 'statut_choices': Terrain.STATUT_CHOICES
    })

@login_required
def admin_ajouter_terrain(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    communes = Commune.objects.all()
    utilisateurs = Utilisateur.objects.filter(role__in=['citoyen', 'professionnel'])
    if request.method == 'POST':
        commune = get_object_or_404(Commune, pk=request.POST.get('commune'))
        terrain = Terrain.objects.create(
            reference_cadastrale=request.POST.get('reference_cadastrale'),
            commune=commune,
            superficie=float(request.POST.get('superficie', 0)),
            statut=request.POST.get('statut', 'libre'),
            adresse_complete=request.POST.get('adresse_complete', ''),
            latitude=float(request.POST.get('latitude', 5.3484)),
            longitude=float(request.POST.get('longitude', -4.0267)),
            zone_usage=request.POST.get('zone_usage', 'residentiel'),
            numero_lot=request.POST.get('numero_lot', ''),
            valeur_estimee=request.POST.get('valeur_estimee') or None,
        )
        prop_id = request.POST.get('proprietaire')
        if prop_id:
            terrain.proprietaire_actuel = Utilisateur.objects.get(pk=prop_id)
            terrain.save()
        HistoriqueTerrain.objects.create(
            terrain=terrain,
            action='Création terrain',
            description=f"Terrain {terrain.reference_cadastrale} créé par {request.user}",
            effectue_par=request.user,
        )
        messages.success(request, f'Terrain {terrain.reference_cadastrale} créé !')
        return redirect('admin_terrains')
    return render(request, 'foncier/admin/ajouter_terrain.html', {
        'communes': communes, 'utilisateurs': utilisateurs,
        'statut_choices': Terrain.STATUT_CHOICES,
        'zone_choices': Terrain._meta.get_field('zone_usage').choices
    })

@login_required
def admin_modifier_terrain(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    terrain = get_object_or_404(Terrain, pk=pk)
    communes = Commune.objects.all()
    utilisateurs = Utilisateur.objects.filter(role__in=['citoyen', 'professionnel'])
    if request.method == 'POST':
        ancien_statut = terrain.statut
        terrain.superficie = float(request.POST.get('superficie', terrain.superficie))
        terrain.statut = request.POST.get('statut', terrain.statut)
        terrain.adresse_complete = request.POST.get('adresse_complete', terrain.adresse_complete)
        terrain.latitude = float(request.POST.get('latitude', terrain.latitude))
        terrain.longitude = float(request.POST.get('longitude', terrain.longitude))
        terrain.zone_usage = request.POST.get('zone_usage', terrain.zone_usage)
        terrain.notes_admin = request.POST.get('notes_admin', terrain.notes_admin)
        prop_id = request.POST.get('proprietaire')
        if prop_id:
            terrain.proprietaire_actuel = Utilisateur.objects.get(pk=prop_id)
        terrain.save()
        if ancien_statut != terrain.statut:
            HistoriqueTerrain.objects.create(
                terrain=terrain,
                action='Changement de statut',
                description=f"Statut changé de {ancien_statut} à {terrain.statut}",
                effectue_par=request.user,
            )
        messages.success(request, 'Terrain mis à jour !')
        return redirect('admin_terrains')
    return render(request, 'foncier/admin/modifier_terrain.html', {
        'terrain': terrain, 'communes': communes, 'utilisateurs': utilisateurs,
        'statut_choices': Terrain.STATUT_CHOICES,
        'zone_choices': Terrain._meta.get_field('zone_usage').choices
    })

@login_required
def admin_demandes(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    statut = request.GET.get('statut', '')
    demandes = DemandeProcedure.objects.select_related('terrain', 'demandeur').order_by('-date_soumission')
    if statut:
        demandes = demandes.filter(statut=statut)
    return render(request, 'foncier/admin/demandes.html', {
        'demandes': demandes, 'statut_choices': DemandeProcedure.STATUT_CHOICES
    })

@login_required
def admin_detail_demande(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    demande = get_object_or_404(DemandeProcedure, pk=pk)
    if request.method == 'POST':
        demande.statut = request.POST.get('statut', demande.statut)
        demande.commentaire_admin = request.POST.get('commentaire_admin', '')
        demande.save()
        messages.success(request, 'Demande mise à jour !')
        return redirect('admin_demandes')
    return render(request, 'foncier/admin/detail_demande.html', {
        'demande': demande, 'statut_choices': DemandeProcedure.STATUT_CHOICES
    })

@login_required
def admin_utilisateurs(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    users = Utilisateur.objects.all().order_by('-date_joined')
    return render(request, 'foncier/admin/utilisateurs.html', {'users': users})

@login_required
def admin_reclamations(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    reclamations = Reclamation.objects.select_related('terrain', 'plaignant').order_by('-date_depot')
    return render(request, 'foncier/admin/reclamations.html', {'reclamations': reclamations})

@login_required
def admin_alertes(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    alertes = Alerte.objects.select_related('terrain').filter(est_active=True).order_by('-date_creation')
    return render(request, 'foncier/admin/alertes.html', {'alertes': alertes})

@login_required
def admin_stats(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    from django.db.models.functions import TruncMonth
    stats = {
        'par_statut': list(Terrain.objects.values('statut').annotate(count=Count('id'))),
        'par_commune': list(Terrain.objects.values('commune__nom').annotate(count=Count('id'))[:10]),
        'par_zone': list(Terrain.objects.values('zone_usage').annotate(count=Count('id'))),
        'demandes_par_type': list(DemandeProcedure.objects.values('type_demande').annotate(count=Count('id'))),
        'total_terrains': Terrain.objects.count(),
        'total_demandes': DemandeProcedure.objects.count(),
        'total_reclamations': Reclamation.objects.count(),
        'total_utilisateurs': Utilisateur.objects.count(),
    }
    return render(request, 'foncier/admin/statistiques.html', {'stats': stats})

# ===== API ENDPOINTS =====
def api_terrains(request):
    terrains = Terrain.objects.select_related('commune').all()
    commune_id = request.GET.get('commune')
    statut = request.GET.get('statut')
    if commune_id:
        terrains = terrains.filter(commune__id=commune_id)
    if statut:
        terrains = terrains.filter(statut=statut)
    
    COLOR_MAP = {
        'libre': '#22c55e',
        'titre_foncier': '#3b82f6',
        'acd': '#f59e0b',
        'litige': '#ef4444',
        'reserve_etat': '#8b5cf6',
        'lotissement': '#06b6d4',
        'vendu': '#6b7280',
    }
    
    data = []
    for t in terrains:
        data.append({
            'id': t.id,
            'reference': t.reference_cadastrale,
            'lat': t.latitude,
            'lng': t.longitude,
            'statut': t.statut,
            'statut_label': t.get_statut_display(),
            'couleur': COLOR_MAP.get(t.statut, '#6b7280'),
            'superficie': t.superficie,
            'commune': t.commune.nom if t.commune else '',
            'adresse': t.adresse_complete,
            'alerte': t.alerte_active,
            'geojson': t.geojson,
        })
    return JsonResponse({'terrains': data})

def api_terrain_detail(request, pk):
    terrain = get_object_or_404(Terrain, pk=pk)
    return JsonResponse({
        'id': terrain.id,
        'reference': terrain.reference_cadastrale,
        'statut': terrain.statut,
        'statut_label': terrain.get_statut_display(),
        'superficie': terrain.superficie,
        'commune': terrain.commune.nom if terrain.commune else '',
        'adresse': terrain.adresse_complete,
        'proprietaire': str(terrain.proprietaire_actuel) if terrain.proprietaire_actuel else 'Non renseigné',
        'zone_usage': terrain.get_zone_usage_display(),
        'valeur_estimee': terrain.valeur_estimee,
        'alerte': terrain.alerte_active,
        'lat': terrain.latitude,
        'lng': terrain.longitude,
    })

def api_communes(request):
    communes = Commune.objects.all()
    data = [{'id': c.id, 'nom': c.nom, 'lat': c.latitude, 'lng': c.longitude} for c in communes]
    return JsonResponse({'communes': data})

def api_stats(request):
    from django.db.models import Count
    return JsonResponse({
        'total_terrains': Terrain.objects.count(),
        'par_statut': list(Terrain.objects.values('statut').annotate(n=Count('id'))),
        'total_demandes': DemandeProcedure.objects.count(),
        'alertes_actives': Alerte.objects.filter(est_active=True).count(),
    })

@login_required
def rapport_terrain(request, pk):
    terrain = get_object_or_404(Terrain, pk=pk)
    historique = terrain.historique.all()[:8]
    alertes = terrain.alertes.filter(est_active=True)
    return render(request, 'foncier/rapport_terrain.html', {
        'terrain': terrain, 'historique': historique, 'alertes': alertes
    })

def api_notifications(request):
    """Notifications pour l'utilisateur connecté"""
    if not request.user.is_authenticated:
        return JsonResponse({'notifications': []})
    notifs = []
    demandes_recentes = DemandeProcedure.objects.filter(
        demandeur=request.user,
        date_modification__gte=__import__('django.utils.timezone', fromlist=['now']).now() - __import__('datetime').timedelta(days=7)
    ).order_by('-date_modification')[:5]
    for d in demandes_recentes:
        notifs.append({
            'type': 'demande',
            'message': f"Demande {d.reference} : {d.get_statut_display()}",
            'url': f'/dashboard/demandes/{d.pk}/',
            'date': d.date_modification.strftime('%d/%m/%Y'),
        })
    return JsonResponse({'notifications': notifs, 'count': len(notifs)})

import csv
from django.http import HttpResponse

@login_required
def export_terrains_csv(request):
    """Export CSV de tous les terrains (admin) ou terrain propre (citoyen)"""
    response = HttpResponse(content_type='text/csv; charset=utf-8')
    response['Content-Disposition'] = 'attachment; filename="terrains_akwabafoncier.csv"'
    response.write('\ufeff')  # BOM UTF-8 pour Excel
    writer = csv.writer(response, delimiter=';')
    writer.writerow(['Référence', 'Commune', 'Superficie (m²)', 'Statut', 'Zone', 'Propriétaire', 'Latitude', 'Longitude', 'Adresse', 'Valeur (FCFA)', 'Alerte'])
    if is_admin(request.user):
        terrains = Terrain.objects.select_related('commune', 'proprietaire_actuel').all()
    else:
        terrains = Terrain.objects.filter(proprietaire_actuel=request.user)
    for t in terrains:
        writer.writerow([
            t.reference_cadastrale, t.commune.nom if t.commune else '',
            t.superficie, t.get_statut_display(), t.get_zone_usage_display(),
            str(t.proprietaire_actuel) if t.proprietaire_actuel else '',
            t.latitude, t.longitude, t.adresse_complete,
            t.valeur_estimee or '', 'Oui' if t.alerte_active else 'Non'
        ])
    return response

@login_required
def admin_ajouter_alerte(request):
    if not is_admin(request.user):
        return redirect('dashboard')
    if request.method == 'POST':
        terrain = get_object_or_404(Terrain, pk=request.POST.get('terrain'))
        Alerte.objects.create(
            terrain=terrain,
            type_alerte=request.POST.get('type_alerte'),
            description=request.POST.get('description', ''),
            signale_par=request.user,
        )
        terrain.alerte_active = True
        terrain.save()
        HistoriqueTerrain.objects.create(
            terrain=terrain, action='Alerte créée',
            description=f"Alerte {request.POST.get('type_alerte')} ajoutée par {request.user}",
            effectue_par=request.user,
        )
        messages.success(request, 'Alerte créée avec succès.')
        return redirect('admin_alertes')
    terrains = Terrain.objects.all()
    return render(request, 'foncier/admin/ajouter_alerte.html', {
        'terrains': terrains,
        'type_choices': Alerte._meta.get_field('type_alerte').choices
    })

@login_required
def admin_resoudre_alerte(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    alerte = get_object_or_404(Alerte, pk=pk)
    alerte.est_active = False
    alerte.save()
    # Désactiver alerte terrain si plus d'alertes actives
    if not alerte.terrain.alertes.filter(est_active=True).exists():
        alerte.terrain.alerte_active = False
        alerte.terrain.save()
    messages.success(request, 'Alerte résolue.')
    return redirect('admin_alertes')

@login_required 
def upload_document(request, terrain_pk):
    terrain = get_object_or_404(Terrain, pk=terrain_pk)
    if request.method == 'POST' and request.FILES.get('fichier'):
        from foncier.models import DocumentFoncier
        doc = DocumentFoncier.objects.create(
            terrain=terrain,
            type_document=request.POST.get('type_document', 'autre'),
            titre=request.POST.get('titre', 'Document'),
            fichier=request.FILES['fichier'],
            date_document=request.POST.get('date_document') or __import__('datetime').date.today(),
            uploade_par=request.user,
            est_officiel=is_admin(request.user),
        )
        HistoriqueTerrain.objects.create(
            terrain=terrain, action='Document ajouté',
            description=f"Document '{doc.titre}' ajouté",
            effectue_par=request.user,
        )
        messages.success(request, f'Document "{doc.titre}" uploadé avec succès.')
    return redirect('detail_terrain', pk=terrain_pk)

@login_required
def admin_update_reclamation(request, pk):
    if not is_admin(request.user):
        return redirect('dashboard')
    reclamation = get_object_or_404(Reclamation, pk=pk)
    if request.method == 'POST':
        reclamation.statut = request.POST.get('statut', reclamation.statut)
        reclamation.commentaire_admin = request.POST.get('commentaire_admin', '')
        reclamation.save()
        messages.success(request, 'Réclamation mise à jour.')
    return redirect('admin_reclamations')
