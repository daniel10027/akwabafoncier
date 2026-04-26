# 🏛️ AkwabaFoncier
**Plateforme nationale de transparence, de sécurisation et de gestion intelligente du foncier en Côte d'Ivoire**

---

## 🚀 Installation rapide

### Prérequis
- Python 3.10+
- pip
- PostgreSQL (ou SQLite pour le développement)

### 1. Cloner et installer
```bash
cd akwabafoncier
pip install -r requirements.txt
```

### 2. Configuration
Copier et modifier le fichier de configuration :
```bash
cp akwabafoncier/settings.py akwabafoncier/settings_local.py
# Modifier les paramètres DATABASE, SECRET_KEY, etc.
```

### 3. Base de données
```bash
python manage.py migrate
python manage.py createsuperuser
```

### 4. Données de démonstration
```bash
python manage.py shell < fixtures/demo_data.py
```

### 5. Lancer le serveur
```bash
python manage.py runserver
```

L'application est accessible sur http://127.0.0.1:8000

---

## 👤 Comptes de démonstration

| Utilisateur | Mot de passe | Rôle |
|---|---|---|
| admin | admin123 | Super Administrateur |
| adminop | admin123 | Admin Opérationnel |
| citoyen0 | test123 | Citoyen |

---

## 🏗️ Architecture du projet

```
akwabafoncier/
├── akwabafoncier/          # Configuration Django
│   ├── settings.py
│   └── urls.py
├── core/                   # App principale (landing, pages publiques)
├── foncier/                # App foncier (terrains, demandes, réclamations)
│   ├── models.py           # Terrain, Commune, Demande, Réclamation, Alerte
│   ├── views.py            # Vues citoyen + admin complet
│   └── urls.py
├── cartographie/           # App cartographie SIG
├── paiements/              # App paiements (CinetPay, Orange Money, Wave)
├── utilisateurs/           # App utilisateurs (auth, profils, rôles)
├── static/
│   ├── css/akwaba.css      # Design system Côte d'Ivoire
│   └── js/akwaba.js
├── templates/              # Tous les templates HTML
│   ├── base.html           # Template de base
│   ├── base_dashboard.html # Template avec sidebar
│   ├── core/               # Landing, contact, tarifs
│   ├── foncier/            # Dashboard, terrains, demandes
│   │   └── admin/          # Interface administrateur
│   ├── cartographie/       # Carte Leaflet interactive
│   ├── paiements/          # Paiements, abonnements
│   └── utilisateurs/       # Login, register, profil
└── manage.py
```

---

## 🎯 Fonctionnalités complètes

### Espace Citoyen
- ✅ Tableau de bord personnalisé
- ✅ Carte interactive SIG (Leaflet.js) avec 7 couches de statut
- ✅ Vérification de terrain avant achat
- ✅ Fiche terrain complète (historique, documents, alertes)
- ✅ Demandes administratives en ligne (ACD, TF, morcellement)
- ✅ Suivi de dossier en temps réel
- ✅ Dépôt de réclamations
- ✅ Gestion de profil

### Espace Administrateur
- ✅ Dashboard avec statistiques et graphiques (Chart.js)
- ✅ Gestion CRUD complète des terrains
- ✅ Localisation cartographique à l'ajout
- ✅ Traitement des demandes (approbation/rejet)
- ✅ Gestion des réclamations
- ✅ Tableau des alertes actives
- ✅ Gestion des utilisateurs
- ✅ Statistiques détaillées avec 4 graphiques

### Cartographie SIG
- ✅ Carte Leaflet.js interactive
- ✅ Marqueurs colorés par statut juridique
- ✅ 3 couches de fond (Plan, Satellite, Topo)
- ✅ Panel d'information terrain au clic
- ✅ Filtres par statut et commune
- ✅ Recherche par référence cadastrale
- ✅ Visualisation densité (heatmap)
- ✅ Export CSV des terrains visibles
- ✅ Contrôle d'échelle
- ✅ Légende interactive
- ✅ Compteurs de statuts en temps réel

### Paiements
- ✅ Orange Money
- ✅ MTN MoMo
- ✅ Wave
- ✅ Carte bancaire (CinetPay)
- ✅ Abonnements Pro (mensuel/annuel/entreprise)
- ✅ Historique des transactions
- ✅ Notification de paiement (webhook)

---

## 🐘 Configuration PostgreSQL (production)

```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': 'akwabafoncier_db',
        'USER': 'akwaba_user',
        'PASSWORD': 'your_secure_password',
        'HOST': 'localhost',
        'PORT': '5432',
    }
}
```

```sql
CREATE DATABASE akwabafoncier_db;
CREATE USER akwaba_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE akwabafoncier_db TO akwaba_user;
```

---

## 🌐 Déploiement (Nginx + Gunicorn)

```bash
pip install gunicorn
gunicorn akwabafoncier.wsgi:application --bind 0.0.0.0:8000 --workers 3
```

```nginx
server {
    listen 80;
    server_name akwabafoncier.ci www.akwabafoncier.ci;

    location /static/ {
        alias /path/to/akwabafoncier/staticfiles/;
    }

    location /media/ {
        alias /path/to/akwabafoncier/media/;
    }

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

---

## 💳 Intégration CinetPay

```python
# settings.py
CINETPAY_API_KEY = 'votre-cle-api'
CINETPAY_SITE_ID = 'votre-site-id'
CINETPAY_NOTIFY_URL = 'https://akwabafoncier.ci/paiements/notify/'
CINETPAY_RETURN_URL = 'https://akwabafoncier.ci/paiements/retour/'
```

---

## 🎨 Design System

Couleurs Côte d'Ivoire :
- 🟠 Orange principal: `#F77F00`
- ⚪ Blanc: `#FFFFFF`
- 🟢 Vert: `#009B55`

Polices :
- Titres: Sora (Google Fonts)
- Corps: DM Sans (Google Fonts)

---

## 📞 Contact & Hackathon SIADE 2026

**AkwabaFoncier** — Projet présenté au Salon International de l'Agri-Elevage et de la Digitalisation en Afrique (SIADE) 2026.

> *"La terre est un patrimoine national. Sa gestion doit être claire, juste et accessible à tous."*
