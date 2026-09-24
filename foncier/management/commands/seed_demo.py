"""
Commande Django pour créer les comptes et données de démonstration
Utilisation: python manage.py seed_demo
"""
import random
from datetime import timedelta

from django.core.management.base import BaseCommand
from django.utils import timezone

from foncier.models import Terrain, DemandeProcedure, Reclamation, Alerte, HistoriqueTerrain
from paiements.models import TarifService, Transaction
from utilisateurs.models import Utilisateur


class Command(BaseCommand):
    help = "Crée les comptes de démonstration et des données réalistes (demandes, réclamations, alertes, tarifs)"

    def handle(self, *args, **options):
        self.stdout.write("Création des comptes de démonstration...")
        admin = self._ensure_user('admin', 'admin123', 'super_admin', 'Awa', 'Kouassi', is_staff=True, is_superuser=True)
        adminop = self._ensure_user('adminop', 'admin123', 'admin_operationnel', 'Serge', 'Diabaté', is_staff=True)
        citoyens = []
        prenoms = ['Fatou', 'Koffi', 'Aminata', 'Yao', 'Aya', 'Ibrahim', 'Mariam', 'Jean-Baptiste', 'Adjoua', 'Moussa']
        noms = ['Traoré', 'Konaté', 'Bamba', 'Ouattara', 'N\'Guessan', 'Coulibaly', 'Kra', 'Yao', 'Dosso', 'Kouamé']
        for i in range(10):
            u = self._ensure_user(
                f'citoyen{i}', 'test123', 'citoyen',
                prenoms[i], noms[i],
                telephone=f'07{random.randint(10000000, 99999999)}',
            )
            citoyens.append(u)
        pro = self._ensure_user('proimmo', 'test123', 'professionnel', 'Cabinet', 'Foncier Plus', telephone='0102030405')

        self.stdout.write("Attribution de propriétaires aux terrains...")
        terrains = list(Terrain.objects.all())
        for t in terrains:
            if not t.proprietaire_actuel and t.statut in ('titre_foncier', 'vendu', 'acd') and random.random() < 0.6:
                t.proprietaire_actuel = random.choice(citoyens)
                t.save()

        self.stdout.write("Création des tarifs de service...")
        tarifs = [
            ('verification_basique', 1000, "Vérification instantanée du statut légal d'un terrain."),
            ('rapport_complet', 5000, "Rapport PDF complet : historique, documents, alertes et propriété."),
            ('historique_complet', 3000, "Historique complet des transactions et évolutions du terrain."),
            ('certificat_verification', 7500, "Certificat officiel de vérification opposable aux tiers."),
            ('depot_acd', 15000, "Frais de dossier pour une demande d'Arrêté de Concession Définitive."),
            ('depot_titre', 25000, "Frais de dossier pour une demande de Titre Foncier."),
            ('depot_morcellement', 20000, "Frais de dossier pour une demande de morcellement de parcelle."),
            ('depot_reclamation', 2000, "Frais de traitement d'une réclamation ou d'un signalement."),
            ('abonnement_pro_mensuel', 15000, "Accès illimité aux vérifications et rapports, facturé au mois."),
            ('abonnement_pro_annuel', 150000, "Accès illimité aux vérifications et rapports, facturé à l'année (2 mois offerts)."),
            ('abonnement_entreprise', 500000, "Accès multi-utilisateurs, API dédiée et support prioritaire."),
        ]
        for service, prix, description in tarifs:
            TarifService.objects.update_or_create(
                service=service, defaults={'prix': prix, 'description': description, 'est_actif': True}
            )

        self.stdout.write("Création des demandes de démonstration...")
        type_choices = [c[0] for c in DemandeProcedure.TYPE_CHOICES]
        statut_choices = [c[0] for c in DemandeProcedure.STATUT_CHOICES]
        descriptions = [
            "Demande de régularisation suite à acquisition familiale.",
            "Constitution du dossier pour obtention du titre définitif.",
            "Morcellement du terrain en 3 lots pour héritiers.",
            "Mutation de propriété suite à acte de vente notarié.",
            "Demande de duplicata suite à perte du document original.",
        ]
        if not DemandeProcedure.objects.exists():
            for i in range(18):
                terrain = random.choice(terrains)
                demandeur = random.choice(citoyens)
                d = DemandeProcedure.objects.create(
                    type_demande=random.choice(type_choices),
                    terrain=terrain,
                    demandeur=demandeur,
                    statut=random.choice(statut_choices),
                    description=random.choice(descriptions),
                )
                DemandeProcedure.objects.filter(pk=d.pk).update(
                    date_soumission=timezone.now() - timedelta(days=random.randint(1, 120))
                )

        self.stdout.write("Création des réclamations de démonstration...")
        objets = [
            "Vente suspecte constatée sur ce terrain",
            "Empiètement de la parcelle voisine",
            "Document de propriété falsifié présenté par un tiers",
            "Litige de bornage avec un voisin",
            "Occupation illégale du terrain",
        ]
        rec_statuts = [c[0] for c in Reclamation.STATUT_CHOICES]
        if not Reclamation.objects.exists():
            for i in range(9):
                terrain = random.choice(terrains)
                Reclamation.objects.create(
                    terrain=terrain,
                    plaignant=random.choice(citoyens),
                    objet=random.choice(objets),
                    description_detaillee="Signalement déposé via la plateforme AkwabaFoncier pour vérification par les services compétents.",
                    statut=random.choice(rec_statuts),
                )

        self.stdout.write("Création des alertes actives...")
        alerte_types = [c[0] for c in Alerte.TYPE_CHOICES]
        litige_terrains = [t for t in terrains if t.statut == 'litige'] or terrains
        if not Alerte.objects.exists():
            for t in litige_terrains[:8]:
                Alerte.objects.create(
                    terrain=t,
                    type_alerte=random.choice(alerte_types),
                    description="Alerte générée automatiquement suite à signalement citoyen ou contrôle administratif.",
                    signale_par=random.choice(citoyens),
                    est_active=True,
                )
                t.alerte_active = True
                t.save()

        self.stdout.write("Création d'un historique de terrain...")
        if not HistoriqueTerrain.objects.exists():
            for t in random.sample(terrains, min(15, len(terrains))):
                HistoriqueTerrain.objects.create(
                    terrain=t,
                    action='Enregistrement initial',
                    description=f"Terrain {t.reference_cadastrale} enregistré dans le système cadastral.",
                    effectue_par=admin,
                )

        self.stdout.write("Création de transactions de démonstration...")
        if not Transaction.objects.exists():
            verif = TarifService.objects.get(service='verification_basique')
            rapport = TarifService.objects.get(service='rapport_complet')
            for i in range(10):
                tarif = random.choice([verif, rapport])
                Transaction.objects.create(
                    utilisateur=random.choice(citoyens),
                    service=tarif,
                    terrain=random.choice(terrains),
                    montant=tarif.prix,
                    methode_paiement=random.choice(['orange_money', 'mtn_momo', 'wave', 'cinetpay']),
                    statut=random.choice(['succes', 'succes', 'succes', 'en_attente']),
                )

        self.stdout.write(self.style.SUCCESS(
            "Données de démonstration prêtes : "
            f"{Utilisateur.objects.count()} utilisateurs, {Terrain.objects.count()} terrains, "
            f"{DemandeProcedure.objects.count()} demandes, {Reclamation.objects.count()} réclamations, "
            f"{Alerte.objects.filter(est_active=True).count()} alertes actives."
        ))

    def _ensure_user(self, username, password, role, first_name, last_name, is_staff=False, is_superuser=False, telephone=''):
        user, created = Utilisateur.objects.get_or_create(
            username=username,
            defaults={
                'role': role,
                'first_name': first_name,
                'last_name': last_name,
                'email': f'{username}@akwabafoncier.ci',
                'is_staff': is_staff,
                'is_superuser': is_superuser,
                'est_verifie': True,
                'telephone': telephone,
            },
        )
        if created:
            user.set_password(password)
            user.save()
        return user
