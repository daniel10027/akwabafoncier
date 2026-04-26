from django.db import models
from utilisateurs.models import Utilisateur

class Commune(models.Model):
    nom = models.CharField(max_length=100)
    code = models.CharField(max_length=20, unique=True)
    region = models.CharField(max_length=100, default='')
    latitude = models.FloatField(default=5.3484)
    longitude = models.FloatField(default=-4.0267)
    
    def __str__(self):
        return self.nom

class Quartier(models.Model):
    nom = models.CharField(max_length=100)
    commune = models.ForeignKey(Commune, on_delete=models.CASCADE, related_name='quartiers')
    
    def __str__(self):
        return f"{self.nom} - {self.commune.nom}"

class Terrain(models.Model):
    STATUT_CHOICES = [
        ('libre', 'Libre / Disponible'),
        ('titre_foncier', 'Titré (Titre Foncier)'),
        ('acd', 'ACD en cours'),
        ('litige', 'En Litige'),
        ('reserve_etat', 'Réservé État'),
        ('lotissement', 'Lotissement en cours'),
        ('vendu', 'Vendu / Transféré'),
    ]
    
    reference_cadastrale = models.CharField(max_length=50, unique=True)
    commune = models.ForeignKey(Commune, on_delete=models.SET_NULL, null=True)
    quartier = models.ForeignKey(Quartier, on_delete=models.SET_NULL, null=True, blank=True)
    superficie = models.FloatField(help_text='Superficie en m²')
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='libre')
    proprietaire_actuel = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True, blank=True, related_name='terrains_possedes')
    adresse_complete = models.TextField(blank=True)
    latitude = models.FloatField()
    longitude = models.FloatField()
    geojson = models.TextField(blank=True, help_text='Données GeoJSON du contour')
    numero_lot = models.CharField(max_length=50, blank=True)
    ilot = models.CharField(max_length=50, blank=True)
    zone_usage = models.CharField(max_length=50, default='residentiel', choices=[
        ('residentiel', 'Résidentiel'),
        ('commercial', 'Commercial'),
        ('industriel', 'Industriel'),
        ('agricole', 'Agricole'),
        ('mixte', 'Mixte'),
    ])
    valeur_estimee = models.BigIntegerField(null=True, blank=True, help_text='Valeur en FCFA')
    date_enregistrement = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    notes_admin = models.TextField(blank=True)
    alerte_active = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.reference_cadastrale} - {self.commune}"

class DocumentFoncier(models.Model):
    TYPE_CHOICES = [
        ('titre_foncier', 'Titre Foncier'),
        ('acd', 'ACD'),
        ('plan_bornage', 'Plan de Bornage'),
        ('acte_vente', 'Acte de Vente'),
        ('permis_construire', 'Permis de Construire'),
        ('certificat_propriete', 'Certificat de Propriété'),
        ('autre', 'Autre'),
    ]
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='documents')
    type_document = models.CharField(max_length=30, choices=TYPE_CHOICES)
    titre = models.CharField(max_length=200)
    fichier = models.FileField(upload_to='documents_fonciers/')
    date_document = models.DateField()
    date_upload = models.DateTimeField(auto_now_add=True)
    uploade_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    est_officiel = models.BooleanField(default=False)
    
    def __str__(self):
        return f"{self.type_document} - {self.terrain.reference_cadastrale}"

class HistoriqueTerrain(models.Model):
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='historique')
    action = models.CharField(max_length=200)
    description = models.TextField()
    effectue_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    date_action = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-date_action']

class DemandeProcedure(models.Model):
    TYPE_CHOICES = [
        ('acd', 'Demande ACD'),
        ('titre_foncier', 'Demande Titre Foncier'),
        ('morcellement', 'Morcellement'),
        ('mutation', 'Mutation / Transfert'),
        ('duplicata', 'Duplicata'),
    ]
    STATUT_CHOICES = [
        ('soumise', 'Soumise'),
        ('en_cours', 'En cours de traitement'),
        ('complement_requis', 'Complément requis'),
        ('approuvee', 'Approuvée'),
        ('rejetee', 'Rejetée'),
        ('finalisee', 'Finalisée'),
    ]
    
    reference = models.CharField(max_length=30, unique=True)
    type_demande = models.CharField(max_length=30, choices=TYPE_CHOICES)
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='demandes')
    demandeur = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='demandes')
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='soumise')
    description = models.TextField()
    commentaire_admin = models.TextField(blank=True)
    date_soumission = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    date_finalisation = models.DateField(null=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.reference:
            import random, string
            self.reference = 'AKW-' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.reference} - {self.type_demande}"

class Reclamation(models.Model):
    STATUT_CHOICES = [
        ('deposee', 'Déposée'),
        ('en_analyse', 'En analyse'),
        ('mediation', 'En médiation'),
        ('transmise_justice', 'Transmise à la justice'),
        ('resolue', 'Résolue'),
        ('classee', 'Classée sans suite'),
    ]
    
    reference = models.CharField(max_length=30, unique=True)
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='reclamations')
    plaignant = models.ForeignKey(Utilisateur, on_delete=models.CASCADE, related_name='reclamations')
    objet = models.CharField(max_length=300)
    description_detaillee = models.TextField()
    statut = models.CharField(max_length=30, choices=STATUT_CHOICES, default='deposee')
    commentaire_admin = models.TextField(blank=True)
    date_depot = models.DateTimeField(auto_now_add=True)
    date_modification = models.DateTimeField(auto_now=True)
    
    def save(self, *args, **kwargs):
        if not self.reference:
            import random, string
            self.reference = 'REC-' + ''.join(random.choices(string.digits, k=8))
        super().save(*args, **kwargs)

class Alerte(models.Model):
    TYPE_CHOICES = [
        ('fraude_suspectee', 'Fraude suspectée'),
        ('vente_multiple', 'Vente multiple détectée'),
        ('document_falsifie', 'Document falsifié'),
        ('litige_actif', 'Litige actif'),
        ('non_conformite', 'Non-conformité'),
    ]
    terrain = models.ForeignKey(Terrain, on_delete=models.CASCADE, related_name='alertes')
    type_alerte = models.CharField(max_length=30, choices=TYPE_CHOICES)
    description = models.TextField()
    signale_par = models.ForeignKey(Utilisateur, on_delete=models.SET_NULL, null=True)
    est_active = models.BooleanField(default=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.type_alerte} - {self.terrain.reference_cadastrale}"
