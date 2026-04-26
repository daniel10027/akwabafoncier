#!/bin/bash
# ==============================================
# AkwabaFoncier — Script de déploiement
# Usage: bash deploy.sh
# ==============================================

set -e

echo "🏛️  AkwabaFoncier — Déploiement"
echo "================================"

# Couleurs
GREEN='\033[0;32m'
ORANGE='\033[0;33m'
RED='\033[0;31m'
NC='\033[0m'

ok()   { echo -e "${GREEN}✅ $1${NC}"; }
info() { echo -e "${ORANGE}ℹ️  $1${NC}"; }
err()  { echo -e "${RED}❌ $1${NC}"; exit 1; }

# 1. Vérifier Python
python3 --version >/dev/null 2>&1 || err "Python 3 requis"
ok "Python détecté"

# 2. Créer env virtuel si absent
if [ ! -d "venv" ]; then
    info "Création de l'environnement virtuel..."
    python3 -m venv venv
    ok "Environnement virtuel créé"
fi

source venv/bin/activate

# 3. Installer les dépendances
info "Installation des dépendances..."
pip install -r requirements.txt -q
ok "Dépendances installées"

# 4. Copier .env si absent
if [ ! -f ".env" ]; then
    cp .env.example .env
    info "Fichier .env créé — modifiez les variables avant de continuer"
    echo ""
    echo "Éditez .env puis relancez : bash deploy.sh"
    exit 0
fi

# 5. Migrations
info "Migrations de la base de données..."
python manage.py migrate --noinput
ok "Migrations effectuées"

# 6. Collecte des fichiers statiques
info "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput -v 0
ok "Fichiers statiques collectés"

# 7. Créer superuser si première fois
python manage.py shell -c "
from utilisateurs.models import Utilisateur
if not Utilisateur.objects.filter(is_superuser=True).exists():
    import os
    Utilisateur.objects.create_superuser(
        username=os.getenv('ADMIN_USERNAME', 'admin'),
        email=os.getenv('ADMIN_EMAIL', 'admin@akwabafoncier.ci'),
        password=os.getenv('ADMIN_PASSWORD', 'ChangeMe2026!'),
        role='super_admin', est_verifie=True
    )
    print('Superuser créé')
else:
    print('Superuser déjà existant')
" 2>/dev/null

ok "Administrateur prêt"

echo ""
echo "========================================"
ok "Déploiement terminé avec succès !"
echo "========================================"
echo ""
echo "Démarrer le serveur de développement :"
echo "  python manage.py runserver"
echo ""
echo "Démarrer en production avec Gunicorn :"
echo "  gunicorn akwabafoncier.wsgi:application --bind 0.0.0.0:8000 --workers 3"
echo ""
echo "🌐 Application : http://localhost:8000"
echo "🔑 Admin Django : http://localhost:8000/admin/"
echo ""
