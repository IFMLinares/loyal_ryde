import json
from django.core.management.base import BaseCommand
from apps.loyalRyde.models import Rates, Route, DeparturePoint, ArrivalPoint, FleetType
from apps.loyalRyde.models_zones import Zone, ZoneRate
from django.db import transaction

class Command(BaseCommand):
    help = 'Migra los datos de Rates a ZoneRate usando estados como zonas.'

    def handle(self, *args, **kwargs):
        migrated = 0
        skipped = 0
        with transaction.atomic():
            for rate in Rates.objects.all():
                try:
                    route = rate.route
                    dep = DeparturePoint.objects.get(pk=route.departure_point_id)
                    arr = ArrivalPoint.objects.get(pk=route.arrival_point_id)
                    origin_zone = Zone.objects.filter(name=dep.state).first()
                    destination_zone = Zone.objects.filter(name=arr.state).first()
                    type_vehicle = rate.type_vehicle
                    if not origin_zone or not destination_zone:
                        self.stdout.write(self.style.WARNING(f"No se encontró Zone para: {dep.state} o {arr.state}. Rate ID: {rate.pk}"))
                        skipped += 1
                        continue
                    ZoneRate.objects.update_or_create(
                        origin=origin_zone,
                        destination=destination_zone,
                        type_vehicle=type_vehicle,
                        defaults={
                            'service_type': rate.service_type,
                            'price': rate.price,
                            'price_round_trip': rate.price_round_trip,
                            'driver_gain': rate.driver_gain,
                            'driver_price': rate.driver_price,
                            'driver_price_round_trip': rate.driver_price_round_trip,
                            'gain_loyal_ride': rate.gain_loyal_ride,
                            'gain_loyal_ride_round_trip': rate.gain_loyal_ride_round_trip,
                            'daytime_waiting_time': rate.daytime_waiting_time,
                            'nightly_waiting_time': rate.nightly_waiting_time,
                            'driver_daytime_waiting_time': rate.driver_daytime_waiting_time,
                            'driver_nightly_waiting_time': rate.driver_nightly_waiting_time,
                            'driver_gain_waiting_time': rate.driver_gain_waiting_time,
                            'detour_local': rate.detour_local,
                            'driver_gain_detour_local': rate.driver_gain_detour_local,
                            'driver_gain_detour_local_quantity': rate.driver_gain_detour_local_quantity,
                        }
                    )
                    migrated += 1
                except Exception as e:
                    self.stdout.write(self.style.ERROR(f"Error migrando Rate ID {rate.pk}: {e}"))
                    skipped += 1
        self.stdout.write(self.style.SUCCESS(f"Migración finalizada. Migrados: {migrated}, Omitidos: {skipped}"))
