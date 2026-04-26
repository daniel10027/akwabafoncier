from django.shortcuts import render
from django.contrib.auth.decorators import login_required

@login_required
def carte_principale(request):
    return render(request, 'cartographie/carte.html')
