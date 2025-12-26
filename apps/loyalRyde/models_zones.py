from django.db import models
from django.contrib.gis.db import models as gis_models
import json
from django.contrib.gis.geos import GEOSGeometry, MultiPolygon
from decimal import Decimal
from .models import FleetType


class Zone(gis_models.Model):
    name = gis_models.CharField(max_length=100, unique=True)
    polygon = gis_models.MultiPolygonField(srid=4326)
    is_special = gis_models.BooleanField(default=False)

    def __str__(self) -> str:
        return self.name

    class Meta:
        verbose_name = 'Zona'
        verbose_name_plural = 'Zonas'


class ZoneRate(models.Model):
    SERVICE_TYPE_CHOICES = [
        ('traslado', 'Traslado Ejecutivo'),
        ('encomienda', 'Encomienda'),
        ('conductor', 'Conductor'),
    ]

    origin = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='origin_rates')
    destination = models.ForeignKey('Zone', on_delete=models.CASCADE, related_name='destination_rates')
    # Clasificación por vehículo
    type_vehicle = models.ForeignKey(FleetType, on_delete=models.CASCADE, null=True, blank=True)
    # Tipo de servicio (opcional, según negocio)
    service_type = models.CharField(max_length=50, choices=SERVICE_TYPE_CHOICES, blank=True, null=True)

    # Precios base
    price = models.DecimalField(max_digits=10, decimal_places=2)
    price_round_trip = models.DecimalField(max_digits=10, decimal_places=2)

    # Ganancias/participaciones
    driver_gain = models.DecimalField(max_digits=5, decimal_places=2, help_text='Porcentaje %')
    driver_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_price_round_trip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gain_loyal_ride = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    gain_loyal_ride_round_trip = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    # Esperas
    daytime_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    nightly_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_daytime_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_nightly_waiting_time = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_gain_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Porcentaje %')

    # Desvíos
    detour_local = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    driver_gain_detour_local = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, help_text='Porcentaje %')
    driver_gain_detour_local_quantity = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    class Meta:
        unique_together = ('origin', 'destination', 'type_vehicle')
        verbose_name = 'Tarifa de Zona'
        verbose_name_plural = 'Tarifas de Zonas'

    def __str__(self) -> str:
        veh = self.type_vehicle.type if self.type_vehicle else 'N/A'
        return f"{self.origin} → {self.destination} ({veh})"

    def save(self, *args, **kwargs):
        # Cálculos derivados basados en porcentajes
        try:
            if self.driver_gain is not None:
                dg = Decimal(self.driver_gain) / Decimal('100')
                if self.price is not None:
                    self.driver_price = Decimal(self.price) * dg
                    self.gain_loyal_ride = Decimal(self.price) - (self.driver_price or Decimal('0'))
                if self.price_round_trip is not None:
                    self.driver_price_round_trip = Decimal(self.price_round_trip) * dg
                    self.gain_loyal_ride_round_trip = Decimal(self.price_round_trip) - (self.driver_price_round_trip or Decimal('0'))

            if self.detour_local is not None and self.driver_gain_detour_local is not None:
                dgl = Decimal(self.driver_gain_detour_local) / Decimal('100')
                self.driver_gain_detour_local_quantity = Decimal(self.detour_local) * dgl

            if self.daytime_waiting_time is not None and self.driver_gain_waiting_time is not None:
                dwg = Decimal(self.driver_gain_waiting_time) / Decimal('100')
                self.driver_daytime_waiting_time = Decimal(self.daytime_waiting_time) * dwg

            if self.nightly_waiting_time is not None and self.driver_gain_waiting_time is not None:
                nwg = Decimal(self.driver_gain_waiting_time) / Decimal('100')
                self.driver_nightly_waiting_time = Decimal(self.nightly_waiting_time) * nwg
        except Exception:
            # No bloquear guardado por errores de conversión
            pass

        super().save(*args, **kwargs)


class PricingConfig(models.Model):
    base_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_km = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    per_min = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    min_fare = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    nocturnal_multiplier = models.DecimalField(max_digits=10, decimal_places=2, default=1)
    airport_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    tolls_surcharge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def __str__(self) -> str:
        return 'Configuración de precios'

    class Meta:
        verbose_name = 'Configuración de Precios'
        verbose_name_plural = 'Configuraciones de Precios'


class ZoneUpload(models.Model):
    """Modelo simple para que el staff cargue un GeoJSON desde el admin
    y se importen/actualicen las zonas sin usar consola.
    """
    file = models.FileField(upload_to='geojson/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carga de GeoJSON de Zonas'
        verbose_name_plural = 'Cargas de GeoJSON de Zonas'

    def __str__(self) -> str:
        return f"GeoJSON {self.pk} ({self.uploaded_at:%Y-%m-%d %H:%M})"

    def process(self):
        self.file.seek(0)
        data = json.load(self.file)
        for feat in data.get('features', []):
            props = feat.get('properties') or {}
            name = props.get('name')
            is_special = bool(props.get('is_special', False))
            geom = GEOSGeometry(json.dumps(feat['geometry']))
            if geom.geom_type == 'Polygon':
                geom = MultiPolygon(geom)
            Zone.objects.update_or_create(
                name=name,
                defaults={'polygon': geom, 'is_special': is_special}
            )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        # Procesar inmediatamente después de guardar el archivo
        try:
            self.process()
        except Exception:
            # Evitar romper el guardado por errores de formato; el admin mostrará el error en logs
            pass
