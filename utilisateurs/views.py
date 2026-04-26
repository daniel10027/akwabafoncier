from django.shortcuts import render, redirect
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Utilisateur

def login_view(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            return redirect(request.GET.get('next', 'dashboard'))
        else:
            messages.error(request, 'Identifiants incorrects.')
    return render(request, 'utilisateurs/login.html')

def logout_view(request):
    logout(request)
    return redirect('landing')

def register_view(request):
    if request.method == 'POST':
        data = request.POST
        if Utilisateur.objects.filter(username=data.get('username')).exists():
            messages.error(request, 'Ce nom d\'utilisateur existe déjà.')
            return render(request, 'utilisateurs/register.html')
        user = Utilisateur.objects.create_user(
            username=data.get('username'),
            email=data.get('email'),
            password=data.get('password'),
            first_name=data.get('first_name', ''),
            last_name=data.get('last_name', ''),
            telephone=data.get('telephone', ''),
            role=data.get('role', 'citoyen'),
        )
        login(request, user)
        messages.success(request, 'Compte créé avec succès. Bienvenue sur AkwabaFoncier !')
        return redirect('dashboard')
    return render(request, 'utilisateurs/register.html')

@login_required
def profil_view(request):
    if request.method == 'POST':
        user = request.user
        user.first_name = request.POST.get('first_name', user.first_name)
        user.last_name = request.POST.get('last_name', user.last_name)
        user.telephone = request.POST.get('telephone', user.telephone)
        user.adresse = request.POST.get('adresse', user.adresse)
        if request.FILES.get('photo'):
            user.photo = request.FILES['photo']
        user.save()
        messages.success(request, 'Profil mis à jour.')
    return render(request, 'utilisateurs/profil.html', {'user': request.user})
