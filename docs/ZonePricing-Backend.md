# Guía Paso a Paso: Detección de Zonas y Motor de Precios en Backend

Esta guía te lleva, de forma incremental, a implementar precios por zonas (Caracas, Catia La Mar, Aeropuerto de La Guaira, etc.), con fallback por distancia/tiempo cuando no exista una tarifa exacta. La detección se hace en backend usando GeoDjango/PostGIS.

## 0. Prerrequisitos
- PostgreSQL 13+ con PostGIS (Windows): instala PostgreSQL y agrega la extensión PostGIS desde el instalador oficial.
- Variables y claves: Google Maps API con Distance Matrix/Directions habilitado.
- Paquetes Python: agrega `Django>=4`, `psycopg2-binary`, `django.contrib.gis`.

## 1. Activar GeoDjango y PostGIS
- En [settings/settings.py](settings/settings.py):
  - Añade `django.contrib.gis` a `INSTALLED_APPS`.
- En tu configuración de base de datos (p. ej. [settings/db.py](settings/db.py)):
  - Usa `ENGINE = 'django.contrib.gis.db.backends.postgis'` y asegura `NAME`, `USER`, `PASSWORD`, `HOST`, `PORT`.
- En PostgreSQL, dentro de tu base de datos:

```sql
CREATE EXTENSION IF NOT EXISTS postgis;
```

## 2. Modelos de Zonas y Tarifas
Crearemos modelos dedicados para zonas y tarifas zona→zona, manteniendo `Rates` para catálogos existentes.

### 2.1 `Zone`
Representa polígonos de áreas (Caracas urbana, Catia La Mar, Aeropuerto, etc.).

```python
from django.contrib.gis.db import models as gis_models

class Zone(gis_models.Model):
    name = gis_models.CharField(max_length=100, unique=True)
    polygon = gis_models.MultiPolygonField(srid=4326)  # WGS84
    is_special = gis_models.BooleanField(default=False)  # Aeropuerto, peaje, etc.

    def __str__(self):
        return self.name
```

### 2.2 `ZoneRate`
Tarifa base por par de zonas y tipo de servicio.

```python
class ZoneRate(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('traslado', 'Traslado Ejecutivo'),
        ('encomienda', 'Encomienda'),
        ('conductor', 'Conductor'),
    ]

    origin = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='origin_rates')
    destination = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='destination_rates')
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_round_trip = models.DecimalField(max_digits=10, decimal_places=2)
    daytime_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nightly_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    detour_local = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('origin', 'destination', 'service_type')

    def __str__(self):
        return f"{self.origin} → {self.destination} ({self.service_type})"
```

### 2.3 `PricingConfig` (opcional)
Parámetros del fallback (fórmula dinámica por km/min, mínimos y recargos).

```python
class PricingConfig(models.Model):
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nocturnal_multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    airport_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tolls_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self):
        return "PricingConfig"
```

## 3. Migraciones

```bash
python manage.py makemigrations
python manage.py migrate
```

## 4. Importar Zonas desde GeoJSON
Guarda tus polígonos en `docs/geojson/zones.geojson` con propiedades `name` e `is_special` si aplica.

### 4.1 Comando de gestión (sugerido)
Crea un comando `import_zones` que lea GeoJSON y cree `Zone`s.

```python
# apps/loyalRyde/management/commands/import_zones.py
import json
from django.core.management.base import BaseCommand
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from apps.loyalRyde.models import Zone

class Command(BaseCommand):
    help = 'Importa zonas desde GeoJSON'

    def add_arguments(self, parser):
        parser.add_argument('--file', required=True)

    def handle(self, *args, **opts):
        with open(opts['file'], 'r', encoding='utf-8') as f:
            data = json.load(f)
        for feat in data['features']:
            name = feat['properties'].get('name')
            is_special = bool(feat['properties'].get('is_special', False))
            geom = GEOSGeometry(json.dumps(feat['geometry']))
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            Zone.objects.update_or_create(name=name, defaults={'polygon': geom, 'is_special': is_special})
        self.stdout.write(self.style.SUCCESS('Zonas importadas'))
```

Ejecuta:

```bash
python manage.py import_zones --file docs/geojson/zones.geojson
```

## 5. Detección de Zona (Backend)
Crea un helper para mapear lat/lng a `Zone` vía point-in-polygon.

```python
# apps/loyalRyde/services/pricing.py
from django.contrib.gis.geos import Point
from apps.loyalRyde.models import Zone, ZoneRate, PricingConfig

def locate_zone(lat, lng):
    p = Point(float(lng), float(lat), srid=4326)
    return Zone.objects.filter(polygon__contains=p).first()

def find_zone_rate(origin_zone, dest_zone, service_type):
    if not origin_zone or not dest_zone:
        return None
    return ZoneRate.objects.filter(origin=origin_zone, destination=dest_zone, service_type=service_type).first()
```

## 6. Fallback por Distancia/Tiempo
Cuando no exista `ZoneRate`, calcula precio con Google Distance Matrix/Directions.

```python
import requests
from decimal import Decimal

def distance_duration(origin_lat, origin_lng, dest_lat, dest_lng, api_key):
    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': f'{origin_lat},{origin_lng}',
        'destinations': f'{dest_lat},{dest_lng}',
        'key': api_key
    }
    r = requests.get(url, params=params).json()
    row = r['rows'][0]['elements'][0]
    dist_km = row['distance']['value'] / 1000.0
    dur_min = row['duration']['value'] / 60.0
    return dist_km, dur_min

def compute_fallback_price(dist_km, dur_min, config: PricingConfig, is_nocturnal=False, airport=False, tolls=False):
    base = Decimal(config.base_fare)
    per_km = Decimal(config.per_km) * Decimal(dist_km)
    per_min = Decimal(config.per_min) * Decimal(dur_min)
    subtotal = base + per_km + per_min
    if is_nocturnal:
        subtotal *= Decimal(config.nocturnal_multiplier)
    if airport:
        subtotal += Decimal(config.airport_surcharge)
    if tolls:
        subtotal += Decimal(config.tolls_surcharge)
    return max(subtotal, Decimal(config.min_fare))
```

Fórmula: $$P = P_{base} + \alpha \cdot d + \beta \cdot t + S$$ donde $d$ son km, $t$ minutos y $S$ recargos.

## 7. Integración con `rates_ajax`
En tu vista de precios (p. ej. `core:rates_ajax`), aplica esta estrategia:

1. Geocodifica origen y destino (ya los tienes en [static/ruta.js](static/ruta.js)).
2. Detecta zonas con `locate_zone()`.
3. Busca `ZoneRate`. Si existe, responde como hoy.
4. Si no existe, calcula fallback y devuelve `estimated_rate` con desglose y banderas (ida y vuelta, extras, desvíos).

Respuesta sugerida:

```json
{
  "rates": [ ... ],
  "estimated_rate": {
    "price": 42.50,
    "price_round_trip": 75.00,
    "breakdown": {"base": 10, "per_km": 25, "per_min": 7.5, "surcharges": 0},
    "source": "fallback"
  }
}
```

## 8. POIs y Overrides
- Marca zonas especiales (`is_special=True`) para Aeropuerto de Maiquetía (nacional e internacional) y aplica recargos/tarifas fijas.
- Puedes crear un modelo `SpecialLocation` si requieres reglas por POI puntual distinto a zonas.

## 9. Admin y Herramientas
- Registra `Zone`, `ZoneRate`, `PricingConfig` en Django Admin.
- Agrega un log de rutas sin coincidencia para alimentar creación de nuevas `ZoneRate`.

## 10. Tests
- Unit Tests: funciones `locate_zone`, `find_zone_rate`, `compute_fallback_price`.
- Integración: vista `rates_ajax` con mocks de Distance Matrix.

## 11. Despliegue Progresivo
1. Crea `PricingConfig` con valores conservadores.
2. Importa zonas críticas (Caracas, Catia La Mar, La Guaira/Aeropuerto).
3. Define `ZoneRate` para rutas más frecuentes.
4. Activa fallback y monitorea logs de “no coincidente”.
5. Ajusta parámetros y agrega nuevas zonas/tarifas.

## 12. Ajustes en el Frontend (mínimos)
- En [templates/loyal_ryde_system/transfer_request/transfer_rerquest.html](templates/loyal_ryde_system/transfer_request/transfer_rerquest.html) y [static/ruta.js](static/ruta.js):
  - Si `estimated_rate` llega vacío, muestra mensaje actual.
  - Si llega con datos, renderiza “Tarifa estimada” como opción (con badge indicando que es estimado) y aplica los extras (desvíos, ida y vuelta).

---

Siguiente acción sugerida: crear los modelos `Zone`, `ZoneRate`, `PricingConfig` y el comando `import_zones`, luego integrar la detección y fallback en la vista `rates_ajax`. 