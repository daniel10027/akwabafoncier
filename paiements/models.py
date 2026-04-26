from django.db import models
from utilisateurs.models import Utilisateur
from foncier.models import Terrain, DemandeProcedure

class TarifService(models.Model):
    SERVICE_CHOICES = [
        ('verification_basique', 'Vérification basique'),
        ('rapport_complet', 'Rapport complet du terrain'),
        ('historique_complet', 'Historique complet'),
        ('certificat_verification', 'Certificat de vérification officiel'),
        ('depot_acd', 'Dépôt demande ACD'),
        ('depot_titre', 'Dépôt demande Titre Foncier'),
        ('depot_morcellement', 'Dépôt morcellement'),
        ('depot_reclamation', 'Dépôt réclamation'),
        ('abonnement_pro_mensuel', 'Abonnement Pro Mensuel'),
        ('abonnement_pro_annuel', 'Abonnement Pro Annuel'),
        ('abonnement_entreprise', 'Abonnement Entreprise'),
    ]
    service = models.CharField(max_length=50, choices=SERVICE_CHOICES, unique=True)
    prix = models.IntegerField(help_text='Prix en FCFA')
    description = models.TextField()
    est_actif = models.BooleanField(default=True)
    
    def __str__(self):
        return f"{self.service} - {self.prix} FCFA"

class Transaction(models.Model):
    STATUT_CHOICES = [
        ('en_attente', 'En attente'),
        ('succes', 'Succès'),
        ('echec', 'Échec'),
        ('rembourse', 'Remboursé'),
    ]
    METHODE_CHOICES = [
        ('cinetpay', 'CinetPay'),
        ('orange_money', 'Orange Money'),
        ('mtn_momo', 'MTN MoMo'),
        ('wave', 'Wave'),
        ('carte_bancaire', 'Carte Bancaire'),
    ]
    
    reference = models.CharField(max_length=50, unique=True)
    utilisateur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='transactions')
    service = models.ForeignKey(TarifService, on_delete=models.SET_NULL, null=True)
    terrain = models.ForeignKey(Terrain, on_delete=models.SET_NULL, null=True, blank=True)
    demande = models.ForeignKey(DemandeProcedure, on_delete=models.SET_NULL, null=True, blank=True)
    montant = models.IntegerField(help_text='Montant en FCFA')
    methode_paiement = models.CharField(max_length=30, choices=METHODE_CHOICES, blank=True)
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='en_attente')
    transaction_id_externe = models.CharField(max_length=100, blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    date_confirmation = models.DateTimeField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.reference:
            import random, string
            self.reference = 'PAY-' + ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
        super().save(*args, **kwargs)

class AbonnementPro(models.Model):
    PLAN_CHOICES = [
        ('mensuel', 'Mensuel'),
        ('annuel', 'Annuel'),
        ('entreprise', 'Entreprise'),
    ]
    utilisateur = models.OneToOneField(Utilisateur, on_delete=models.CASCADE, related_name='abonnement')
    plan = models.CharField(max_length=20, choices=PLAN_CHOICES)
    est_actif = models.BooleanField(default=True)
    date_debut = models.DateField()
    date_fin = models.DateField()
    transaction = models.ForeignKey(Transaction, on_delete=models.SET_NULL, null=True)
    
    def __str__(self):
        return f"{self.utilisateur} - {self.plan}"
