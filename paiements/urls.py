from django.urls import path
from . import views

urlpatterns = [
    path('', views.liste_transactions, name='transactions'),
    path('payer/', views.initier_paiement, name='initier_paiement'),
    path('notify/', views.notify_paiement, name='notify_paiement'),
    path('retour/', views.retour_paiement, name='retour_paiement'),
    path('abonnement/', views.abonnement, name='abonnement'),
]
