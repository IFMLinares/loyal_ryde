from django.contrib import admin
from .models import TransferRequest, Company, AbstractUser, CustomUser, CustomUserDriver, TransferStop,Desviation, ArrivalPoint, DeparturePoint, PeopleTransfer, Rates, Route, DiscountCoupon, FleetType
from .models_zones import Zone, ZoneRate, PricingConfig, ZoneUpload
from leaflet.admin import LeafletGeoAdmin
# Register your models here.

admin.site.register(DiscountCoupon)
admin.site.register(CustomUser)
admin.site.register(Company)
admin.site.register(CustomUserDriver)
admin.site.register(TransferStop)
admin.site.register(Desviation)
admin.site.register(ArrivalPoint)
admin.site.register(DeparturePoint)
admin.site.register(PeopleTransfer)
admin.site.register(Rates)
admin.site.register(Route)
@admin.register(Zone)
class ZoneAdmin(LeafletGeoAdmin):
    list_display = ("name", "is_special")
    search_fields = ("name",)

admin.site.register(ZoneRate)
admin.site.register(PricingConfig)
admin.site.register(ZoneUpload)
admin.site.register(FleetType)

@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'hour', 'payment_method',)
    list_filter = ('payment_method', 'in_town', 'outside_town')
    search_fields = ('departure_site', 'destination')
    # Puedes personalizar más opciones aquí si lo deseas
