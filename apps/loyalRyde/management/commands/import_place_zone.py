import json
import urllib.parse
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from django.core.management.base import BaseCommand, CommandError
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

from apps.loyalRyde.models_zones import Zone


class Command(BaseCommand):
    help = (
        "Importa una Zona a partir de un lugar en OpenStreetMap usando Nominatim. "
        "Útil para aeropuertos, instituciones, parques, campus, etc."
    )

    def add_arguments(self, parser):
        parser.add_argument("--q", required=True, help="Consulta de búsqueda (nombre del lugar)")
        parser.add_argument(
            "--country",
            default="ve",
            help="Código ISO del país para restringir la búsqueda (ej. 've' Venezuela)",
        )
        parser.add_argument("--index", type=int, default=0, help="Índice del resultado a usar (por defecto 0)")
        parser.add_argument("--name", help="Nombre de la Zona (si se omite, usa display_name del resultado)")
        parser.add_argument("--special", action="store_true", help="Marca la zona como especial")
        parser.add_argument(
            "--reset-existing",
            action="store_true",
            help="Si existe una zona con el mismo nombre, la borra antes de crear",
        )

    def _search_nominatim(self, q: str, country: str) -> list:
        params = {
            "q": q,
            "format": "json",
            "polygon_geojson": 1,
            "addressdetails": 1,
            "namedetails": 1,
            "countrycodes": country,
            "limit": 10,
        }
        url = "https://nominatim.openstreetmap.org/search?" + urllib.parse.urlencode(params)
        req = Request(url, headers={"User-Agent": "LoyalRyde/NominatimImport"})
        try:
            with urlopen(req, timeout=30) as resp:
                raw = resp.read().decode("utf-8")
                data = json.loads(raw)
                return data
        except (HTTPError, URLError) as e:
            raise CommandError(f"Error consultando Nominatim: {e}")
        except json.JSONDecodeError as e:
            raise CommandError(f"Respuesta inválida de Nominatim: {e}")

    def handle(self, *args, **opts):
        q = opts["q"]
        country = opts.get("country", "ve")
        index = int(opts.get("index", 0))
        name_override = opts.get("name")
        is_special = bool(opts.get("special", False))
        reset_existing = bool(opts.get("reset_existing", False))

        results = self._search_nominatim(q, country)
        if not results:
            raise CommandError("Nominatim no devolvió resultados para la consulta.")

        if index < 0 or index >= len(results):
            raise CommandError(f"Índice {index} fuera de rango. Resultados disponibles: {len(results)}")

        item = results[index]
        display_name = item.get("display_name")
        geojson = item.get("geojson")
        if not geojson:
            raise CommandError("El resultado no contiene geometría (geojson).")

        # Preferir un nombre corto si está disponible
        namedetails = item.get("namedetails") or {}
        short_name = namedetails.get("name")
        zone_name = name_override or short_name or display_name or q
        # Truncar a máximo 100 caracteres para cumplir el modelo
        if zone_name and len(zone_name) > 100:
            zone_name = zone_name[:100]
        if not zone_name:
            raise CommandError("No se pudo determinar nombre para la Zona.")

        geom = GEOSGeometry(json.dumps(geojson))
        if geom.geom_type == "Polygon":
            geom = MultiPolygon(geom)

        if reset_existing:
            Zone.objects.filter(name=zone_name).delete()

        obj, created = Zone.objects.update_or_create(
            name=zone_name,
            defaults={"polygon": geom, "is_special": is_special},
        )

        self.stdout.write(
            self.style.SUCCESS(
                f"Zona {'creada' if created else 'actualizada'}: {obj.name} (especial={is_special})."
            )
        )
