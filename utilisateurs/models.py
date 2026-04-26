from django.contrib.auth.models import AbstractUser
from django.db import models

class Utilisateur(AbstractUser):
    ROLE_CHOICES = [
        ('citoyen', 'Citoyen'),
        ('professionnel', 'Professionnel'),
        ('admin_operationnel', 'Admin Opérationnel'),
        ('super_admin', 'Super Administrateur'),
    ]
    role = models.CharField(max_length=30, choices=ROLE_CHOICES, default='citoyen')
    telephone = models.CharField(max_length=20, blank=True)
    adresse = models.TextField(blank=True)
    piece_identite = models.CharField(max_length=50, blank=True)
    numero_piece = models.CharField(max_length=50, blank=True)
    photo = models.ImageField(upload_to='profils/', blank=True, null=True)
    est_verifie = models.BooleanField(default=False)
    date_creation = models.DateTimeField(auto_now_add=True)
    
    def is_admin(self):
        return self.role in ['admin_operationnel', 'super_admin']
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.role})"
