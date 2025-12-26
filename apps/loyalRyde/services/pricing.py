from decimal import Decimal
import logging
from typing import Optional, Tuple

from django.conf import settings
from django.contrib.gis.db.models.functions import Area, Transform
from django.contrib.gis.geos import Point
from django.db.models import Q

from apps.loyalRyde.models_zones import Zone, ZoneRate, PricingConfig

logger = logging.getLogger(__name__)


def locate_zone(lat: float, lng: float) -> Optional[Zone]:
    """Zona más específica que cubre el punto: ordena por área asc (subzona < zona < estado)."""
    p = Point(float(lng), float(lat), srid=4326)
    logger.debug("[rates_debug] locate_zone for (%.6f, %.6f)", lat, lng)
    z = (
        Zone.objects
        .filter(polygon__covers=p)
        .annotate(area=Area(Transform('polygon', 3857)))
        .order_by('area')
        .first()
    )
    logger.debug("[rates_debug] locate_zone -> %s", z)
    return z

def locate_zones(lat: float, lng: float) -> list[Zone]:
    """Todas las zonas que cubren el punto, ordenadas por menor área (más específicas primero)."""
    p = Point(float(lng), float(lat), srid=4326)
    logger.debug("[rates_debug] locate_zones for (%.6f, %.6f)", lat, lng)
    zs = list(
        Zone.objects
        .filter(polygon__covers=p)
        .annotate(area=Area(Transform('polygon', 3857)))
        .order_by('area')
    )
    logger.debug("[rates_debug] locate_zones -> %s", [z.name for z in zs])
    return zs


def find_zone_rate(origin_zone: Optional[Zone], dest_zone: Optional[Zone], service_type: Optional[str] = None,
                   type_vehicle_id: Optional[int] = None) -> Optional[ZoneRate]:
    if not origin_zone or not dest_zone:
        return None
    qs = ZoneRate.objects.filter(origin=origin_zone, destination=dest_zone)
    if type_vehicle_id:
        qs = qs.filter(type_vehicle_id=type_vehicle_id)
    if service_type:
        qs = qs.filter(service_type=service_type)
    zr = qs.first()
    logger.debug("[rates_debug] find_zone_rate %s->%s veh=%s svc=%s -> %s",
                 getattr(origin_zone, 'name', None), getattr(dest_zone, 'name', None), type_vehicle_id, service_type, getattr(zr, 'id', None))
    return zr

def resolve_zone_rate(o_lat: float, o_lng: float, d_lat: float, d_lng: float,
                      service_type: Optional[str] = None,
                      type_vehicle_id: Optional[int] = None) -> Optional[ZoneRate]:
    """Intentar encontrar la tarifa más específica combinando listas de zonas (subzona→zona→estado)."""
    o_list = locate_zones(o_lat, o_lng)
    d_list = locate_zones(d_lat, d_lng)
    logger.debug("[rates_debug] resolve_zone_rate: origin_zones=%s dest_zones=%s",
                 [z.name for z in o_list], [z.name for z in d_list])
    for oz in o_list:
        for dz in d_list:
            zr = find_zone_rate(oz, dz, service_type=service_type, type_vehicle_id=type_vehicle_id)
            if zr:
                logger.debug("[rates_debug] resolve_zone_rate matched: %s -> %s => zr_id=%s price=%s",
                             oz.name, dz.name, zr.id, zr.price)
                return zr
    return None


def compute_fallback_price(dist_km: float, dur_min: float, config: PricingConfig,
                           is_nocturnal: bool = False, airport: bool = False, tolls: bool = False) -> Decimal:
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


def distance_duration(origin_lat: float, origin_lng: float, dest_lat: float, dest_lng: float, api_key: Optional[str] = None) -> Tuple[float, float]:
    """Use Google Distance Matrix to get distance (km) and duration (min).
    Note: Keeping import local to avoid hard dependency during tests.
    """
    import requests

    key = api_key or getattr(settings, 'GOOGLE_MAPS_API_KEY', None)
    if not key:
        raise RuntimeError('GOOGLE_MAPS_API_KEY is not configured')

    url = 'https://maps.googleapis.com/maps/api/distancematrix/json'
    params = {
        'origins': f'{origin_lat},{origin_lng}',
        'destinations': f'{dest_lat},{dest_lng}',
        'key': key,
    }
    r = requests.get(url, params=params, timeout=15)
    r.raise_for_status()
    data = r.json()
    row = data['rows'][0]['elements'][0]
    dist_km = row['distance']['value'] / 1000.0
    dur_min = row['duration']['value'] / 60.0
    return dist_km, dur_min
