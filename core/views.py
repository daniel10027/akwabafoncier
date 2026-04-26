from django.shortcuts import render, redirect
from django.http import JsonResponse
from foncier.models import Terrain, DemandeProcedure, Reclamation, Commune
from utilisateurs.models import Utilisateur

def landing(request):
    stats = {
        'terrains': Terrain.objects.count(),
        'demandes': DemandeProcedure.objects.count(),
        'utilisateurs': Utilisateur.objects.filter(role='citoyen').count(),
        'communes': Commune.objects.count(),
    }
    return render(request, 'core/landing.html', {'stats': stats})

def a_propos(request):
    return render(request, 'core/a_propos.html')

def tarifs(request):
    from paiements.models import TarifService
    tarifs = TarifService.objects.filter(est_actif=True)
    return render(request, 'core/tarifs.html', {'tarifs': tarifs})

def contact(request):
    if request.method == 'POST':
        from django.core.mail import send_mail
        send_mail(
            f"Contact AkwabaFoncier - {request.POST.get('sujet')}",
            request.POST.get('message'),
            request.POST.get('email'),
            ['contact@akwabafoncier.ci'],
            fail_silently=True,
        )
        from django.contrib import messages
        messages.success(request, 'Message envoyé avec succès !')
        return redirect('contact')
    return render(request, 'core/contact.html')
