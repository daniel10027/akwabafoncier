# 🏛️ AkwabaFoncier
**Plateforme nationale de transparence, de sécurisation et de gestion intelligente du foncier en Côte d'Ivoire**

---

## 🐳 Démarrage rapide (Docker, recommandé)

La façon la plus simple de lancer toute la stack (Django + PostgreSQL), migrations et données de démonstration comprises :

```bash
git clone https://github.com/daniel10027/akwabafoncier.git
cd akwabafoncier
docker compose up --build
```

C'est tout. Au premier démarrage, le conteneur `web` attend que PostgreSQL soit prêt, applique les migrations, charge les communes/quartiers/terrains de démonstration (`foncier/data/*.json`) et crée les comptes de démo via `python manage.py seed_demo` automatiquement, à chaque `up`. L'application est accessible sur **http://localhost:8000**.

```bash
docker compose down        # arrêter
docker compose down -v     # arrêter et repartir d'une base vide
docker compose logs -f web # suivre les logs de l'application
```

Aucune configuration `.env` n'est requise pour tester en local : des valeurs de développement sûres sont fournies par défaut dans `docker-compose.yml`. Pour activer de vraies intégrations (CinetPay, email), copiez `.env.example` en `.env` à la racine et renseignez vos clés : `docker compose up` les reprendra automatiquement.

---

## 🛠️ Installation manuelle (sans Docker)

### Prérequis
- Python 3.10+ (testé en 3.11)
- pip
- PostgreSQL (ou SQLite pour le développement rapide)

### 1. Cloner et installer
```bash
cd akwabafoncier
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
```

### 2. Configuration
```bash
cp .env.example .env
# Éditer .env : SECRET_KEY, DB_*, etc. (DB_ENGINE=django.db.backends.sqlite3
# et DB_NAME=db.sqlite3 fonctionnent aussi si vous ne voulez pas installer PostgreSQL)
```

### 3. Base de données
```bash
python manage.py migrate
python manage.py createsuperuser   # optionnel, seed_demo crée déjà un admin
```

### 4. Données de démonstration
```bash
python manage.py loaddata foncier/data/commune.json foncier/data/quartier.json foncier/data/terrains_fixture.json
python manage.py seed_demo
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
│   ├── js/akwaba.js
│   ├── js/sw.js            # Service worker (PWA)
│   ├── manifest.json       # Manifeste PWA (icônes, thème, standalone)
│   └── img/                # Icônes PWA générées (192/512/maskable/apple-touch)
├── templates/              # Tous les templates HTML
│   ├── base.html           # Template de base
│   ├── base_dashboard.html # Template avec sidebar
│   ├── core/               # Landing, contact, tarifs
│   ├── foncier/            # Dashboard, terrains, demandes
│   │   └── admin/          # Interface administrateur
│   ├── cartographie/       # Carte Leaflet interactive
│   ├── paiements/          # Paiements, abonnements
│   └── utilisateurs/       # Login, register, profil
├── foncier/
│   ├── data/                            # Fixtures (communes, quartiers, terrains)
│   ├── management/commands/seed_demo.py # Comptes + données de démo
│   └── templatetags/foncier_extras.py   # Filtre `fcfa` (formatage montants)
├── docker/entrypoint.sh    # Migration + fixtures + seed au démarrage du conteneur
├── Dockerfile
├── docker-compose.yml
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
- ✅ Notification de paiement (webhook) **revérifiée côté serveur CinetPay avant validation** (voir Sécurité ci-dessous)

### Version mobile (PWA)
- ✅ Installable depuis le navigateur (Android/Chrome et iOS/Safari, "Ajouter à l'écran d'accueil"), sans passage par un store
- ✅ Manifeste (`static/manifest.json`) : icônes 192/512/512 maskable, couleur de thème `#F77F00`, mode `standalone`
- ✅ Service worker (`static/js/sw.js`) servi à la racine (`/sw.js`) pour une portée sur toute l'app : stale-while-revalidate sur les assets statiques, network-first ailleurs
- ✅ Navigation responsive complète (sidebar en tiroir + hamburger public) testée à 375px et 1440px

---

## 🔒 Sécurité

- `SECRET_KEY`, identifiants base de données et clés API ne sont jamais en dur dans le code : tout passe par `.env` (voir `.env.example`), qui reste hors du dépôt (`.gitignore`).
- Le webhook de confirmation de paiement (`paiements/notify_paiement`) ne fait plus confiance au seul contenu du callback : il revérifie systématiquement la transaction (statut **et** montant) auprès de l'API CinetPay (`/v2/payment/check`) avant de la marquer comme payée. Le retour navigateur (`retour_paiement`) applique la même revérification plutôt que de valider en aveugle. Sans clé CinetPay configurée, la confirmation automatique n'est acceptée qu'en mode `DEBUG` (développement), jamais en production.
- Aucune requête SQL brute : tous les accès aux données passent par l'ORM Django.
- Accès protégés par `@login_required` sur les vues citoyen et administrateur.

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

## 📞 Contact & candidature

**AkwabaFoncier** — Candidat au **Moov Startup Challenge 2026** (Côte d'Ivoire).

Fondateur : **Diyoro Bi Prince**, informaticien développeur ivoirien.
Dossier de candidature complet, pitch deck et checklist de soumission : voir le dossier [`Docs/`](Docs/).

> *"La terre est un patrimoine national. Sa gestion doit être claire, juste et accessible à tous."*
