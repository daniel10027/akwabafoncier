from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from .models import Transaction, TarifService, AbonnementPro
from foncier.models import Terrain
import json

@login_required
def liste_transactions(request):
    transactions = Transaction.objects.filter(utilisateur=request.user).order_by('-date_creation')
    return render(request, 'paiements/transactions.html', {'transactions': transactions})

@login_required
def initier_paiement(request):
    if request.method == 'POST':
        service_slug = request.POST.get('service')
        terrain_id = request.POST.get('terrain_id')
        try:
            tarif = TarifService.objects.get(service=service_slug, est_actif=True)
        except TarifService.DoesNotExist:
            messages.error(request, 'Service non disponible.')
            return redirect('tarifs')
        
        terrain = None
        if terrain_id:
            terrain = Terrain.objects.filter(pk=terrain_id).first()
        
        transaction = Transaction.objects.create(
            utilisateur=request.user,
            service=tarif,
            terrain=terrain,
            montant=tarif.prix,
            statut='en_attente',
        )
        return render(request, 'paiements/paiement.html', {
            'transaction': transaction,
            'tarif': tarif,
        })
    
    tarifs = TarifService.objects.filter(est_actif=True)
    return render(request, 'paiements/choisir_service.html', {'tarifs': tarifs})

@csrf_exempt
def notify_paiement(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            ref = data.get('cpm_trans_id') or data.get('transaction_id')
            if ref:
                t = Transaction.objects.filter(reference=ref).first()
                if t:
                    t.statut = 'succes'
                    t.transaction_id_externe = data.get('payment_token', '')
                    t.date_confirmation = timezone.now()
                    t.save()
                    if t.service and 'abonnement' in t.service.service:
                        from datetime import timedelta, date
                        duree = 365 if 'annuel' in t.service.service else 30
                        AbonnementPro.objects.update_or_create(
                            utilisateur=t.utilisateur,
                            defaults={
                                'plan': 'annuel' if 'annuel' in t.service.service else 'mensuel',
                                'est_actif': True,
                                'date_debut': date.today(),
                                'date_fin': date.today() + timedelta(days=duree),
                                'transaction': t,
                            }
                        )
        except Exception:
            pass
    return JsonResponse({'status': 'ok'})

@login_required
def retour_paiement(request):
    ref = request.GET.get('transaction_id', '')
    transaction = None
    if ref:
        transaction = Transaction.objects.filter(reference=ref, utilisateur=request.user).first()
        if transaction:
            transaction.statut = 'succes'
            transaction.date_confirmation = timezone.now()
            transaction.save()
    messages.success(request, 'Paiement effectué avec succès !')
    return render(request, 'paiements/retour.html', {'transaction': transaction})

@login_required
def abonnement(request):
    tarifs_abo = TarifService.objects.filter(service__startswith='abonnement_', est_actif=True)
    abo_actuel = AbonnementPro.objects.filter(utilisateur=request.user, est_actif=True).first()
    return render(request, 'paiements/abonnement.html', {
        'tarifs': tarifs_abo, 'abonnement': abo_actuel
    })
