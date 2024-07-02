from django.contrib import admin
from .models import TransferRequest, Company, AbstractUser, CustomUser
# Register your models here.

admin.site.register(CustomUser)
admin.site.register(Company)
@admin.register(TransferRequest)
class TransferRequestAdmin(admin.ModelAdmin):
    list_display = ('id', 'date', 'hour', 'payment_method',)
    list_filter = ('payment_method', 'in_town', 'outside_town')
    search_fields = ('departure_site', 'destination')
    # Puedes personalizar más opciones aquí si lo deseas
