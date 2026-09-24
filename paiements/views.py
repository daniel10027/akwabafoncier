import json
import logging

import requests
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt

from foncier.models import Terrain
from .models import Transaction, TarifService, AbonnementPro

logger = logging.getLogger(__name__)

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

def _verify_cinetpay_transaction(reference, montant_attendu):
    """Revérifie un paiement directement auprès de CinetPay avant de le valider.

    Le webhook (et le retour navigateur) ne doivent jamais suffire à eux seuls
    à marquer une transaction comme payée : leur contenu est entièrement
    contrôlable par l'appelant. On ne fait confiance qu'à la réponse de
    l'API CinetPay elle-même (endpoint payment/check), avec le montant en
    plus du statut.
    """
    api_key = getattr(settings, 'CINETPAY_API_KEY', '')
    site_id = getattr(settings, 'CINETPAY_SITE_ID', '')
    if not api_key or not site_id:
        if settings.DEBUG:
            logger.warning(
                "CinetPay non configuré (DEBUG=True) : confirmation acceptée "
                "sans vérification pour %s. Ne jamais autoriser ceci en production.",
                reference,
            )
            return True
        logger.error("CinetPay non configuré : impossible de vérifier %s", reference)
        return False
    try:
        resp = requests.post(
            'https://api-checkout.cinetpay.com/v2/payment/check',
            json={'apikey': api_key, 'site_id': site_id, 'transaction_id': reference},
            timeout=10,
        )
        result = resp.json()
    except (requests.RequestException, ValueError):
        logger.exception("Erreur réseau/format lors de la vérification CinetPay pour %s", reference)
        return False

    if result.get('code') != '00':
        logger.warning("CinetPay: statut non confirmé pour %s (%s)", reference, result.get('message'))
        return False

    montant_confirme = (result.get('data') or {}).get('amount')
    if montant_confirme is not None and int(montant_confirme) != int(montant_attendu):
        logger.warning(
            "CinetPay: montant incohérent pour %s (attendu %s, reçu %s)",
            reference, montant_attendu, montant_confirme,
        )
        return False
    return True


def _confirmer_transaction(transaction, transaction_id_externe=''):
    transaction.statut = 'succes'
    if transaction_id_externe:
        transaction.transaction_id_externe = transaction_id_externe
    transaction.date_confirmation = timezone.now()
    transaction.save()
    if transaction.service and 'abonnement' in transaction.service.service:
        from datetime import timedelta, date
        duree = 365 if 'annuel' in transaction.service.service else 30
        AbonnementPro.objects.update_or_create(
            utilisateur=transaction.utilisateur,
            defaults={
                'plan': 'annuel' if 'annuel' in transaction.service.service else 'mensuel',
                'est_actif': True,
                'date_debut': date.today(),
                'date_fin': date.today() + timedelta(days=duree),
                'transaction': transaction,
            }
        )


@csrf_exempt
def notify_paiement(request):
    if request.method != 'POST':
        return JsonResponse({'status': 'ignored'})

    try:
        data = json.loads(request.body)
    except (json.JSONDecodeError, UnicodeDecodeError):
        logger.warning("notify_paiement: payload JSON invalide")
        return JsonResponse({'status': 'invalid_payload'}, status=400)

    ref = data.get('cpm_trans_id') or data.get('transaction_id')
    if not ref:
        return JsonResponse({'status': 'missing_reference'}, status=400)

    t = Transaction.objects.filter(reference=ref).first()
    if not t:
        logger.warning("notify_paiement: référence inconnue %s", ref)
        return JsonResponse({'status': 'unknown_reference'}, status=404)

    if t.statut == 'succes':
        return JsonResponse({'status': 'already_confirmed'})

    if not _verify_cinetpay_transaction(ref, t.montant):
        return JsonResponse({'status': 'verification_failed'}, status=400)

    _confirmer_transaction(t, transaction_id_externe=data.get('payment_token', ''))
    return JsonResponse({'status': 'ok'})

@login_required
def retour_paiement(request):
    ref = request.GET.get('transaction_id', '')
    transaction = None
    if ref:
        transaction = Transaction.objects.filter(reference=ref, utilisateur=request.user).first()
        if transaction and transaction.statut == 'en_attente':
            # Le retour navigateur n'est qu'une indication : on revérifie
            # toujours auprès de CinetPay avant de considérer le paiement acquis.
            if _verify_cinetpay_transaction(transaction.reference, transaction.montant):
                _confirmer_transaction(transaction)
                transaction.refresh_from_db()
    if transaction and transaction.statut == 'succes':
        messages.success(request, 'Paiement effectué avec succès !')
    elif transaction:
        messages.info(request, "Paiement en cours de confirmation. Vous serez notifié dès sa validation.")
    return render(request, 'paiements/retour.html', {'transaction': transaction})

@login_required
def abonnement(request):
    tarifs_abo = TarifService.objects.filter(service__startswith='abonnement_', est_actif=True)
    abo_actuel = AbonnementPro.objects.filter(utilisateur=request.user, est_actif=True).first()
    return render(request, 'paiements/abonnement.html', {
        'tarifs': tarifs_abo, 'abonnement': abo_actuel
    })
