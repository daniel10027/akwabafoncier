"""
Commande Django pour charger les données OpenStreetMap
Utilisation: python manage.py load_osm_data
"""

import json
from pathlib import Path
from django.core.management.base import BaseCommand
from django.core.exceptions import ObjectDoesNotExist
from foncier.models import Commune, Quartier

class Command(BaseCommand):
    help = 'Charge les communes et quartiers depuis les fichiers JSON OpenStreetMap'

    def add_arguments(self, parser):
        parser.add_argument(
            '--file',
            type=str,
            help='Chemin vers le fichier JSON (par défaut: data/django_communes_quartiers.json)',
            default='data/django_communes_quartiers.json'
        )
        parser.add_argument(
            '--clear',
            action='store_true',
            help='Supprime les données existantes avant import',
        )

    def handle(self, *args, **options):
        file_path = Path(options['file'])

        if not file_path.exists():
            self.stderr.write(self.style.ERROR(f'Fichier {file_path} non trouvé'))
            return

        if options['clear']:
            self.stdout.write('Suppression des données existantes...')
            Quartier.objects.all().delete()
            Commune.objects.all().delete()

        self.stdout.write(f'Chargement des données depuis {file_path}...')

        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)

        communes_count = 0
        quartiers_count = 0

        for item in data:
            if item['model'] == 'foncier.commune':
                try:
                    Commune.objects.create(
                        pk=item['pk'],
                        nom=item['fields']['nom'],
                        code=item['fields']['code'],
                        region=item['fields']['region'],
                        latitude=item['fields']['latitude'],
                        longitude=item['fields']['longitude'],
                    )
                    communes_count += 1
                except Exception as e:
                    self.stderr.write(f'Erreur commune {item["fields"]["nom"]}: {e}')

            elif item['model'] == 'foncier.quartier':
                try:
                    commune = Commune.objects.get(pk=item['fields']['commune'])
                    Quartier.objects.create(
                        pk=item['pk'],
                        nom=item['fields']['nom'],
                        commune=commune,
                    )
                    quartiers_count += 1
                except Exception as e:
                    self.stderr.write(f'Erreur quartier {item["fields"]["nom"]}: {e}')

        self.stdout.write(self.style.SUCCESS(
            f'✅ Import terminé!\n   - Communes: {communes_count}\n   - Quartiers: {quartiers_count}'
        ))
