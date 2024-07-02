from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.conf import settings

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
        ('cancelada', 'Cancelada'),
    ]

TYPES_CHOICES = [
    ('Traslado Ejecutivo', 'Traslado Ejecutivo'),
    ('Encomienda', 'Encomienda'),
    ('Conductor', 'Conductor')
]

ROUTE_TYPE_CHOICES = [
    ('origen', 'origen'),
    ('destino', 'destino')
]

ROUTE_CHOICES = [
    ('Caracas', 'Toda Caracas'),
    ('Arrecife', 'Arrecife'),
    ('Barcelona', 'Barcelona'),
    ('Barquisimeto', 'Barquisimeto'),
    ('Carayaca', 'Carayaca'),
    ('Catia la Mar', 'Catia la Mar'),
    ('Charallave', 'Charallave'),
    ('Cua', 'Cua'),
    ('Guanta', 'Guanta'),
    ('Guarenas', 'Guarenas'),
    ('Guatire', 'Guatire'),
    ('La Guaira', 'La Guaira'),
    ('Los Teques', 'Los Teques'),
    ('Maracay', 'Maracay'),
    ('Moron', 'Moron'),
    ('Ocumare del Tuy', 'Ocumare del Tuy'),
    ('Puerto Cabello', 'Puerto Cabello'),
    ('Puerto La Cruz', 'Puerto La Cruz'),
    ('San Antonio de los Altos', 'San Antonio de los Altos'),
    ('Santa Lucia', 'Santa Lucia'),
    ('Santa Teresa', 'Santa Teresa'),
    ('Monay', 'Monay'),
    ('Valencia', 'Valencia')
]


# Create your models here.
class Company(models.Model):
    name = models.CharField(max_length=256, verbose_name="Nombre de la Empresa", help_text='El nombre de la empresa es obligatorio.')
    email = models.EmailField(unique=True, verbose_name="Correo electrónico", blank=True, null=True, help_text='ingrese el correo electrónico del la empresa, este debe ser unico')
    rif = models.CharField(max_length=256, verbose_name="RIF", unique=True, help_text='RIF es obligatorio')
    address = models.CharField(max_length=256, verbose_name="Dirección", blank=True, null=True, help_text='Dirección es Opcional')
    phone = models.CharField(max_length=18, blank=True, null=True, help_text='Telefono es obligatorio', verbose_name='Teléfono')
    image = models.ImageField(upload_to='company_images/', blank=True, null=True)
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.name}"

class CustomUser(AbstractUser):
    # Añade campos adicionales aquí
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    role = models.CharField(max_length=20, choices=[('supervisor', 'Supervisor'), ('operator', 'Operador'), ('conductor', 'Conductor')], verbose_name='Rol')
    department = models.CharField(max_length=100, blank=True, verbose_name='Departamento')
    travel_approval = models.BooleanField(default=False, verbose_name='Código de aprobación')
    status = models.CharField(verbose_name="Status",max_length=20, default='inactive', choices=[('inactive', 'Inactivo'), ('active', 'Activo'), ('suspended', 'Suspendido')])
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True,)
    class Meta:
        # Asegúrate de definir un related_name único para evitar conflictos
        permissions = (
            ('is_company_user', 'Can perform company user actions'),
            # Otros permisos personalizados aquí
        )

class PeopleTransfer(models.Model):
    name = models.CharField(max_length=255, verbose_name='nombre')
    phone = models.CharField(max_length=255, verbose_name='teléfono')
    company = models.CharField(max_length=255, verbose_name='empresa')


    def __str__(self):
        return f"{self.name} - {self.company}"


    class Meta:
        verbose_name = 'Persona a transferir'
        verbose_name_plural = 'Personas a transferir'

class DeparturePoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Punto de salida")
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Salidas"
    def __str__(self):
        return f"{self.name}"

class ArrivalPoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Punto de Llegada")
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Destinos"
    def __str__(self):
        return f"{self.name}"

class FleetType(models.Model):
    type = models.CharField(max_length=255, verbose_name="Tipo de Vehiculo", blank=True, null=True,)
    def __str__(self):
        return f"{self.type}"

class Fleet(models.Model):
    brand = models.CharField(max_length=256, verbose_name="Marca del Vehiculo", blank=True, null=True)
    model = models.CharField(max_length=256, verbose_name="Modelo del vehiculo", blank=True, null=True)
    color = models.CharField(max_length=256, verbose_name="Color del vehiculo", blank=True, null=True)
    plaque = models.CharField(max_length=256, verbose_name="Nro de placa",)
    passengers_numbers = models.IntegerField(verbose_name="Número maximo de Pasajeros", blank=True, null=True)
    type = models.ForeignKey(FleetType, on_delete=models.CASCADE, verbose_name="Tipo de vehiculo")
    def __str__(self):
        return f"{self.type}: {self.brand} {self.model}. Color: {self.color}. Placa: {self.plaque}. Max. Pasajeros: {self.passengers_numbers}"

class Route(models.Model):
    # route_name = models.CharField(max_length=255, verbose_name="Ruta", blank=True, null=True)
    route_name = models.CharField(max_length=255, verbose_name="Nombre de la ruta")
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True,)
    departure_point = models.ForeignKey(DeparturePoint, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Punto de salida")
    arrival_point = models.ForeignKey(ArrivalPoint, on_delete=models.CASCADE, blank=True, null=True, verbose_name="Punto de destino")
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    def __str__(self):
        return f"{self.route_name}: {self.departure_point}-{self.arrival_point}"
    
class Rates(models.Model):
    # vehicle = models.ForeignKey(Fleet, on_delete=models.CASCADE, verbose_name="Vehiculo", null=True, blank=True)
    type_vehicle = models.ForeignKey(FleetType, on_delete=models.CASCADE, verbose_name="Tipo de vehiculo", null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name="Ruta", blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precio Ida")
    price_round_trip  = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precio Ida y vuelta")
    driver_gain = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor (porcentaje %)")
    driver_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor del conductor Ida(AutoRellenable)", blank=True, null=True)
    driver_price_round_trip = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor del conductor Ida y Vuelta(AutoRellenable)", blank=True, null=True)
    gain_loyal_ride = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia Loyal Ride Ida(AutoRellenable)", blank=True, null=True)
    gain_loyal_ride_round_trip = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia Loyal Ride Ida y vuelta(AutoRellenable)", blank=True, null=True)
    daytime_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Extra: Hora de espera (diurna) C/u", null=True, blank=True)
    nightly_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Extra: Hora de espera (Nocturna) C/u", null=True, blank=True)
    detour_local = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Desvío Local C/u", null=True, blank=True)
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    def save(self, *args, **kwargs):
        # Calculamos el driver_price como el porcentaje de driver_gain aplicado al precio
        self.driver_price = self.price * (self.driver_gain / 100)
        self.gain_loyal_ride = self.price - self.driver_price

        self.driver_price_round_trip = self.price_round_trip * (self.driver_gain / 100)
        self.gain_loyal_ride_round_trip = self.price_round_trip - self.driver_price_round_trip

        super().save(*args, **kwargs)

    def __str__(self):
        return f"Tarifa para {self.route} - Precio base: {self.price}$"

    class Meta:
        verbose_name_plural = "Tarifas"

class TransferRequest(models.Model):
    date = models.DateField(verbose_name="Fecha del traslado")  # DD/MM/AA
    date_created = models.DateTimeField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)
    hour = models.TimeField(verbose_name="Hora")  # Formato 12h
    payment_method = models.PositiveSmallIntegerField(verbose_name="Método de Pago", choices=payment_method_choices)
    ceco_grafo_pedido = models.PositiveIntegerField(verbose_name="CECO/GRAFO/PEDIDO", blank=True, null=True)  # Puede empezar por 0
    division = models.CharField(max_length=255, verbose_name="División", blank=True, null=True)
    in_town = models.BooleanField(verbose_name="Dentro de la localidad")
    outside_town = models.BooleanField(verbose_name="Fuera de la localidad") 
    fly_checkbox = models.BooleanField(default=False, blank=True, null=True, verbose_name="Aeropuesto?")
    airline = models.CharField(max_length=255, verbose_name="Aerolínea", blank=True, null=True)
    flight = models.CharField(max_length=255, verbose_name="Vuelo", blank=True, null=True)
    route_fly = models.CharField(max_length=255, verbose_name="Ruta de vuelo", blank=True, null=True)
    person_to_transfer = models.ManyToManyField(PeopleTransfer, verbose_name="Persona(s) a Transferir")
    service_requested = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario que Llenó el Formulario", blank=True, null=True)
    service_authorize = models.TextField(verbose_name="Autorización del Servicio", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado", blank=True, null=True, default='esperando validación' )
    executive_transfer = models.BooleanField(default=False, blank=True, null=True, verbose_name="Traslado ejecutivo")
    encomienda = models.BooleanField(default=False, blank=True, null=True, verbose_name="Encomienda")
    driver = models.BooleanField(default=False, blank=True, null=True, verbose_name="Conductor")
    destination_route = models.CharField(max_length=256, verbose_name="Destino")
    full_day = models.BooleanField(default=False, blank=True, null=True, verbose_name="full day")
    half_day = models.BooleanField(default=False, blank=True, null=True, verbose_name="full day")
    destination_route = models.CharField(max_length=256, verbose_name="Destino")
    destination_direc = models.CharField(max_length=255, verbose_name="Dirección destino exacta", blank=True, null=True)
    destination_landmark = models.CharField(max_length=255, verbose_name="Punto de referencia", blank=True, null=True)
    departure_site_route = models.CharField(max_length=256, verbose_name="Salida")
    departure_direc = models.CharField(max_length=255, verbose_name="Dirección salida exacta", blank=True, null=True)
    departure_landmark = models.CharField(max_length=255, verbose_name="Punto de referencia", blank=True, null=True)
    rate = models.ForeignKey(Rates, on_delete=models.CASCADE, verbose_name="Tarifa")

    
    def __str__(self):
        return f"Solicitud de Transferencia {self.id}"
    
    class Meta:
        verbose_name = 'Solicitud de traslado'
        verbose_name_plural = 'Solicitudes de traslado'