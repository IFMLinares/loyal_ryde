import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from apps.loyalRyde.models_zones import Zone


class Command(BaseCommand):
    help = 'Importa zonas desde un archivo GeoJSON (features con properties.name e is_special opcional).'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True, help='Ruta a docs/geojson/zones.geojson')

    def handle(self, *args, **opts):
        file_path = opts['file']
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        created = 0
        updated = 0
        for feat in data.get('features', []):
            name = (feat.get('properties') or {}).get('name')
            is_special = bool((feat.get('properties') or {}).get('is_special', False))
            geom = GEOSGeometry(json.dumps(feat['geometry']))
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            obj, was_created = Zone.objects.update_or_create(
                name=name,
                defaults={'polygon': geom, 'is_special': is_special}
            )
            if was_created:
                created += 1
            else:
                updated += 1
        self.stdout.write(self.style.SUCCESS(f'Zonas importadas. Creadas: {created}, Actualizadas: {updated}'))
