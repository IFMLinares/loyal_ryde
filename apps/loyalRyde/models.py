from django.db import models

payment_method_choices = [
        (1, 'CECO/GRAFO/PEDIDO'),
        (2, 'EFECTIVO'),
        (3, 'TARJETA DE CRÉDITO'),
    ]

STATUS_CHOICES = [
        ('esperando validación', 'Esperando Validación'),
        ('validada', 'Validada'),
        ('en proceso', 'En Proceso'),
        ('finalizada', 'Finalizada'),
    ]

# Create your models here.
class PeopleTransfer(models.Model):
    name = models.CharField(max_length=255, verbose_name='nombre')
    phone = models.CharField(max_length=255, verbose_name='teléfono')
    company = models.CharField(max_length=255, verbose_name='empresa')

    class Meta:
        verbose_name = 'Persona a transferir'
        verbose_name_plural = 'Personas a transferir'

class TransferRequest(models.Model):
    date = models.DateField(verbose_name="Fecha")  # DD/MM/AA
    hour = models.TimeField(verbose_name="Hora")  # Formato 12h
    payment_method = models.PositiveSmallIntegerField(
        choices=payment_method_choices,
        verbose_name="Método de Pago"
    )
    ceco_grafo_pedido = models.PositiveIntegerField(
        verbose_name="CECO/GRAFO/PEDIDO"
    )  # Puede empezar por 0
    division = models.CharField(max_length=255, verbose_name="División")
    in_town = models.BooleanField(verbose_name="Dentro de la localidad")
    outside_town = models.BooleanField(verbose_name="Fuera de la localidad") 
    airline = models.CharField(max_length=255, verbose_name="Aerolínea")
    flight = models.CharField(max_length=255, verbose_name="Vuelo")
    route = models.CharField(max_length=255, verbose_name="Ruta")
    person_to_transfer = models.ManyToManyField(
        PeopleTransfer,
        verbose_name="Persona(s) a Transferir"
    )
    departure_site = models.CharField(max_length=255, verbose_name="Lugar de Salida")
    destination = models.CharField(max_length=255, verbose_name="Destino")
    service_requested = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        verbose_name="Usuario que Llenó el Formulario", blank=True, null=True
    )
    service_authorize = models.TextField(verbose_name="Autorización del Servicio", blank=True, null=True)
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='esperando validacion',
        verbose_name="Estado"
    )

    def __str__(self):
        return f"Solicitud de Transferencia {self.id}"
    
    class Meta:
        verbose_name = 'Solicitud de traslado'
        verbose_name_plural = 'Solicitudes de traslado'

