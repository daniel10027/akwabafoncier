#!/bin/sh
set -e

python - <<'PYEOF'
import os
import socket
import time

host = os.environ.get("DB_HOST", "db")
port = int(os.environ.get("DB_PORT", "5432"))
for _ in range(60):
    try:
        with socket.create_connection((host, port), timeout=2):
            break
    except OSError:
        print(f"En attente de la base de donnees {host}:{port}...")
        time.sleep(1)
else:
    raise SystemExit(f"Base de donnees {host}:{port} injoignable apres 60s")
PYEOF

echo "Application des migrations..."
python manage.py migrate --noinput

echo "Chargement des communes, quartiers et terrains de demonstration..."
python manage.py loaddata foncier/data/commune.json foncier/data/quartier.json foncier/data/terrains_fixture.json

echo "Creation des comptes et donnees de demonstration (seed)..."
python manage.py seed_demo

echo "Collecte des fichiers statiques..."
python manage.py collectstatic --noinput >/dev/null 2>&1 || true

exec "$@"
