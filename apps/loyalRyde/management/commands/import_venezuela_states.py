import json
from urllib.request import urlopen, Request
from urllib.error import URLError, HTTPError

from django.core.management.base import BaseCommand, CommandError
from django.db import transaction
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon

from apps.loyalRyde.models_zones import Zone


DEFAULT_URL = (
	"https://raw.githubusercontent.com/wmgeolab/geoBoundaries/main/"
	"releaseData/gbOpen/VEN/ADM1/geoBoundaries-VEN-ADM1.geojson"
)
JSDELIVR_URL = (
	"https://cdn.jsdelivr.net/gh/wmgeolab/geoBoundaries@main/"
	"releaseData/gbOpen/VEN/ADM1/geoBoundaries-VEN-ADM1.geojson"
)


class Command(BaseCommand):
	help = (
		"Importa los ESTADOS de Venezuela (ADM1) desde geoBoundaries con polígonos precisos. "
		"Por defecto usa la URL oficial abierta; se puede forzar otra fuente con --url."
	)

	def add_arguments(self, parser):
		parser.add_argument(
			"--url",
			dest="url",
			default=DEFAULT_URL,
			help="Fuente GeoJSON (por defecto geoBoundaries ADM1 de Venezuela)",
		)
		parser.add_argument(
			"--reset",
			action="store_true",
			help="Borra primero las Zonas con nombres presentes en el GeoJSON antes de importar",
		)

	def _fetch_text(self, url: str) -> str:
		req = Request(url, headers={"User-Agent": "LoyalRyde/Importer"})
		with urlopen(req, timeout=30) as resp:
			return resp.read().decode("utf-8", errors="replace")

	def _try_load_json(self, text: str) -> dict:
		return json.loads(text)

	def _convert_to_media_url(self, url: str) -> str:
		# Convierte raw.githubusercontent a media.githubusercontent para resolver Git LFS
		# Formato raw: https://raw.githubusercontent.com/{owner}/{repo}/{ref}/{path}
		# Formato media: https://media.githubusercontent.com/media/{owner}/{repo}/{ref}/{path}
		if "raw.githubusercontent.com" in url:
			return url.replace("raw.githubusercontent.com/", "media.githubusercontent.com/media/")
		return url

	def handle(self, *args, **opts):
		url = opts.get("url") or DEFAULT_URL
		reset = opts.get("reset", False)

		# Paso 1: intentar URL indicada
		try:
			text = self._fetch_text(url)
			data = self._try_load_json(text)
		except (URLError, HTTPError) as e:
			raise CommandError(f"Error al descargar GeoJSON desde {url}: {e}")
		except json.JSONDecodeError:
			# Detectar puntero Git LFS
			if text.strip().startswith("version https://git-lfs.github.com/spec/v1"):
				media_url = self._convert_to_media_url(url)
				try:
					text2 = self._fetch_text(media_url)
					data = self._try_load_json(text2)
				except Exception:
					# Último intento: jsDelivr
					try:
						text3 = self._fetch_text(JSDELIVR_URL)
						data = self._try_load_json(text3)
					except Exception as e3:
						raise CommandError(
							"No se pudo obtener GeoJSON (Git LFS). Intentos: raw -> media -> jsDelivr fallidos."
						)
			else:
				# Último intento: jsDelivr
				try:
					text3 = self._fetch_text(JSDELIVR_URL)
					data = self._try_load_json(text3)
				except Exception as e3:
					raise CommandError(
						f"GeoJSON inválido desde {url} y jsDelivr también falló: {e3}"
					)

		features = data.get("features") or []
		if not features:
			raise CommandError("El GeoJSON no contiene 'features'.")

		# Preparar nombres de estados a importar
		names = []
		for feat in features:
			props = feat.get("properties") or {}
			name = props.get("shapeName") or props.get("name")
			if not name:
				# Intentar otra propiedad común
				name = props.get("NAME_1") or props.get("NAME")
			if not name:
				# Si no hay nombre, saltar
				continue
			names.append(name)

		if reset and names:
			Zone.objects.filter(name__in=names).delete()

		created = 0
		updated = 0

		with transaction.atomic():
			for feat in features:
				props = feat.get("properties") or {}
				geom_dict = feat.get("geometry")
				if not geom_dict:
					continue

				name = props.get("shapeName") or props.get("name")
				if not name:
					name = props.get("NAME_1") or props.get("NAME")
				if not name:
					continue

				geom = GEOSGeometry(json.dumps(geom_dict))
				if geom.geom_type == "Polygon":
					geom = MultiPolygon(geom)

				obj, was_created = Zone.objects.update_or_create(
					name=name,
					defaults={"polygon": geom, "is_special": False},
				)
				if was_created:
					created += 1
				else:
					updated += 1

		total = Zone.objects.count()
		self.stdout.write(
			self.style.SUCCESS(
				f"Importación completa. Creadas: {created}, Actualizadas: {updated}. Total Zonas: {total}."
			)
		)

