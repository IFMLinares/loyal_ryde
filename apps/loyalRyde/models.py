import json
from datetime import datetime
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db import models
from django.contrib.auth import get_user_model
from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from django.core.serializers import serialize
from decimal import Decimal
from django.core.serializers.json import DjangoJSONEncoder
from django.conf import settings
from django.contrib.auth.models import AnonymousUser
from django.utils import timezone


payment_method_choices = [
        (1, 'CECO/GRAFO/PEDIDO'),
        (2, 'CREDITO'),
        (3, 'TARJETA DE CRÉDITO'),
        (4, 'PAGO MOVIL'),
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

USER_CHOCIES = [
    ('supervisor', 'Supervisor'), 
    ('operator', 'Operador'), 
    ('conductor', 'Conductor'), 
    ('administrador', 'Administrador'),
    ('despachador', 'Despachador')
    ]

# Create your models here.

class FleetType(models.Model):
    type = models.CharField(max_length=255, verbose_name="Tipo de Vehiculo", blank=True, null=True,)
    def __str__(self):
        return f"{self.type}"

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
        return self.user.username

    class Meta:
        verbose_name = 'Compañia'
        verbose_name_plural = 'Compañias'

class CustomUser(AbstractUser):
    # Añade campos adicionales aquí
    phone = models.CharField(max_length=20, blank=True, verbose_name='Teléfono')
    role = models.CharField(max_length=20, choices=USER_CHOCIES, verbose_name='Rol')
    department = models.CharField(max_length=100, blank=True, verbose_name='Departamento')
    travel_approval = models.BooleanField(default=False, verbose_name='Código de aprobación', blank=True, null=True)
    status = models.CharField(verbose_name="Estatus",max_length=20, default='inactive', choices=[('inactive', 'Inactivo'), ('active', 'Activo'), ('suspended', 'Suspendido')])
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='Empresa', null=True, blank=True,)
    class Meta:
        # Asegúrate de definir un related_name único para evitar conflictos
        permissions = (
            ('is_company_user', 'Can perform company user actions'),
            # Otros permisos personalizados aquí
        )
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

class CustomUserDriver(models.Model):
    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE)
    marca = models.CharField(max_length=256, verbose_name="Marca del Vehiculo", blank=True, null=True)
    model = models.CharField(max_length=256, verbose_name="Modelo del vehiculo", blank=True, null=True)
    color = models.CharField(max_length=256, verbose_name="Color del vehiculo", blank=True, null=True)
    plaque = models.CharField(max_length=256, verbose_name="Nro de placa",)
    passengers_numbers = models.IntegerField(verbose_name="Número maximo de Pasajeros", blank=True, null=True)
    type = models.ForeignKey(FleetType, on_delete=models.CASCADE, verbose_name="Tipo de vehiculo")
    image = models.ImageField(upload_to='driver/', blank=True, null=True, verbose_name="Foto")
    license = models.ImageField(upload_to='driver/', blank=True, null=True, verbose_name="Foto")

    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}. Telefono: {self.user.phone} . {self.marca} {self.model} {self.color} {self.plaque}. "

    class Meta:
        verbose_name = 'Usuario Conductor'
        verbose_name_plural = 'Usuarios Conductores'

class OTPCode(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'{self.user.email} - {self.code}'

class PeopleTransfer(models.Model):
    name = models.CharField(max_length=255, verbose_name='nombre')
    phone = models.CharField(max_length=255, verbose_name='teléfono')
    # company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name='empresa', blank=True, null=True)

    def __str__(self):
        return f"{self.name} - {self.company}"


    class Meta:
        verbose_name = 'Persona a transferir'
        verbose_name_plural = 'Personas a transferir'



class DeparturePoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ciudad")
    state = models.CharField(max_length=255, verbose_name="Estado", blank=True, null=True)
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Salidas"

    def __str__(self):
        return f"{self.name} - {self.state}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if DeparturePoint.objects.filter(name=self.name, state=self.state).exists():
            raise ValidationError(f"La combinación de {self.name} y {self.state} ya existe.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

class ArrivalPoint(models.Model):
    name = models.CharField(max_length=255, verbose_name="Ciudad")
    state = models.CharField(max_length=255, verbose_name="Estado", blank=True, null=True)
    date_created = models.DateField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)

    class Meta:
        verbose_name_plural = "Destinos"

    def __str__(self):
        return f"{self.name} - {self.state}"

    def clean(self):
        from django.core.exceptions import ValidationError
        if ArrivalPoint.objects.filter(name=self.name, state=self.state).exists():
            raise ValidationError(f"La combinación de {self.name} y {self.state} ya existe.")

    def save(self, *args, **kwargs):
        self.clean()
        super().save(*args, **kwargs)

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
        return f"{self.route_name}: Desde: {self.departure_point}. Hasta: {self.arrival_point}"

class DiscountCoupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ('percentage', 'Porcentaje'),
        ('fixed', 'Monto Fijo'),
    ]

    code = models.CharField(max_length=50, unique=True, verbose_name="Código")
    discount_type = models.CharField(max_length=10, choices=DISCOUNT_TYPE_CHOICES, verbose_name="Tipo de Descuento")
    discount_value = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Valor del Descuento")
    expiration_date = models.DateField(verbose_name="Fecha de Expiración")
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Empresa")
    usage_limit = models.IntegerField(verbose_name="Límite de Uso")

    def __str__(self):
        return self.code

    def get_discount_type_display(self):
        return dict(self.DISCOUNT_TYPE_CHOICES).get(self.discount_type, self.discount_type)

    def is_valid(self):
        return self.expiration_date > timezone.now()

    class Meta:
        verbose_name = "Cupón de Descuento"
        verbose_name_plural = "Cupones de Descuento"

class Rates(models.Model):
    # vehicle = models.ForeignKey(Fleet, on_delete=models.CASCADE, verbose_name="Vehiculo", null=True, blank=True)
    type_vehicle = models.ForeignKey(FleetType, on_delete=models.CASCADE, verbose_name="Tipo de vehiculo", null=True, blank=True)
    route = models.ForeignKey(Route, on_delete=models.CASCADE, verbose_name="Ruta", blank=True, null=True)
    price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precio Ida")
    price_round_trip  = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precio Ida y vuelta")
    driver_gain = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor % (traslado)")
    driver_price = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor del conductor Ida", blank=True, null=True)
    driver_price_round_trip = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor del conductor Ida y Vuelta", blank=True, null=True)
    gain_loyal_ride = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia Loyal Ride Ida(AutoRellenable)", blank=True, null=True)
    gain_loyal_ride_round_trip = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia Loyal Ride Ida y vuelta(AutoRellenable)", blank=True, null=True)
    daytime_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Extra: Hora de espera (diurna) C/u", null=True, blank=True)
    nightly_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Extra: Hora de espera (Nocturna) C/u", null=True, blank=True)
    driver_daytime_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor por espera diurna", null=True, blank=True)
    driver_nightly_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor por espera nocturna", null=True, blank=True)
    driver_gain_waiting_time = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor por hora de espera %", null=True, blank=True)
    detour_local = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Precio por desvío Local C/u", null=True, blank=True)
    driver_gain_detour_local = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor por desvío local %", null=True, blank=True)
    driver_gain_detour_local_quantity = models.DecimalField(max_digits=5, decimal_places=2, verbose_name="Ganancia del conductor por desvío local", null=True, blank=True)
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

class TransferStop(models.Model):
    start_time = models.TimeField(verbose_name="Hora de inicio", blank=True, null=True)
    end_time = models.TimeField(verbose_name="Hora de finalización", blank=True, null=True)
    total_time = models.DurationField(verbose_name="Tiempo todal de espera", blank=True, null=True)

    def save(self, *args, **kwargs):
            # Convierte start_time y end_time a objetos datetime
            start_datetime = datetime.combine(datetime.today(), self.start_time)
            end_datetime = datetime.combine(datetime.today(), self.end_time)

            # Calcula la diferencia entre start_time y end_time
            if self.start_time and self.end_time:
                self.total_time = end_datetime - start_datetime
            super().save(*args, **kwargs)

    class Meta:
        verbose_name = 'Parada'
        verbose_name_plural = 'Paradas'

class Desviation(models.Model):
    desviation_direc = models.CharField(max_length=255, verbose_name="Dirección de desvio", blank=True, null=True)
    desviation_number = models.IntegerField(verbose_name="Número de desvio", blank=True, null=True, default=0)
    waypoint_number = models.IntegerField(verbose_name="Número de desvio", blank=True, null=True, default=0)
    lat= models.CharField(max_length=255, verbose_name="Latitud", blank=True, null=True)
    long= models.CharField(max_length=255, verbose_name="Longitud", blank=True, null=True)

    class Meta:
        verbose_name = 'Desvio'
        verbose_name_plural = 'Desvios'
    
    def __str__(self):
        return f"{self.id}-{self.desviation_number}-{self.waypoint_number}"

class TransferRequest(models.Model):
    
    STATUS_CHOICES = [
            ('esperando validación', 'Esperando Validación'),
            ('validada', 'Validada'),
            ('aprobada', 'Aprobada'),
            ('en proceso', 'En Proceso'),
            ('finalizada', 'Finalizada'),
            ('cancelada', 'Cancelada'),
        ]
    approved_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True, blank=True, related_name='approved_requests', verbose_name="Aprobado por")
    rate = models.ForeignKey(Rates, on_delete=models.CASCADE, verbose_name="Tarifa")
    service_requested = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name="Usuario que Llenó el Formulario", blank=True, null=True)
    user_driver = models.ForeignKey(CustomUserDriver, on_delete=models.CASCADE, verbose_name="Usuario conductor", blank=True, null=True)
    stop_time = models.ManyToManyField(TransferStop, verbose_name="Pausa del viaje", blank=True, null=True)
    deviation = models.ManyToManyField(Desviation, verbose_name="Desvios", blank=True, null=True)
    date = models.DateField(verbose_name="Fecha del traslado", blank=True, null=True)  # DD/MM/AA
    date_created = models.DateTimeField(verbose_name="Feha de creación", auto_now_add=True, null=True, blank=True)
    hour = models.TimeField(verbose_name="Hora")  # Formato 12h
    payment_method = models.PositiveSmallIntegerField(verbose_name="Método de Pago", choices=payment_method_choices)
    ceco_grafo_pedido = models.PositiveIntegerField(verbose_name="CECO/GRAFO/PEDIDO", blank=True, null=True)
    division = models.CharField(max_length=255, verbose_name="División", blank=True, null=True)
    in_town = models.BooleanField(verbose_name="Dentro de la localidad")
    outside_town = models.BooleanField(verbose_name="Fuera de la localidad") 
    fly_checkbox = models.BooleanField(default=False, blank=True, null=True, verbose_name="Aeropuesto?")
    airline = models.CharField(max_length=255, verbose_name="Aerolínea", blank=True, null=True)
    flight = models.CharField(max_length=255, verbose_name="Vuelo", blank=True, null=True)
    route_fly = models.CharField(max_length=255, verbose_name="Ruta de vuelo", blank=True, null=True)
    person_to_transfer = models.ManyToManyField(PeopleTransfer, verbose_name="Persona(s) a Transferir", blank=True, null=True)
    service_authorize = models.TextField(verbose_name="Autorización del Servicio", blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, verbose_name="Estado", blank=True, null=True, default='esperando validación' )
    executive_transfer = models.BooleanField(default=False, blank=True, null=True, verbose_name="Traslado ejecutivo")
    encomienda = models.BooleanField(default=False, blank=True, null=True, verbose_name="Encomienda")
    driver = models.BooleanField(default=False, blank=True, null=True, verbose_name="Conductor")
    destination_route = models.CharField(max_length=256, verbose_name="Destino", blank=True, null=True)
    full_day = models.BooleanField(default=False, blank=True, null=True, verbose_name="full day")
    half_day = models.BooleanField(default=False, blank=True, null=True, verbose_name="full day")
    destination_direc = models.CharField(max_length=255, verbose_name="Dirección destino exacta", blank=True, null=True)
    destination_landmark = models.CharField(max_length=255, verbose_name="Punto de referencia", blank=True, null=True)
    departure_site_route = models.CharField(max_length=256, verbose_name="Salida", blank=True, null=True)
    departure_direc = models.CharField(max_length=255, verbose_name="Dirección salida exacta", blank=True, null=True)
    departure_landmark = models.CharField(max_length=255, verbose_name="Punto de referencia", blank=True, null=True)
    lat_1 = models.CharField(max_length=255, verbose_name="Latitud Inicio", blank=True, null=True)
    long_1= models.CharField(max_length=255, verbose_name="Longitud Inicio", blank=True, null=True)
    lat_2 = models.CharField(max_length=255, verbose_name="Latitud Final", blank=True, null=True)
    long_2= models.CharField(max_length=255, verbose_name="Longitud Final", blank=True, null=True)
    # company =  models.CharField(max_length=255, verbose_name="Nombre Compañia (Solo texto)", blank=True, null=True)
    company = models.ForeignKey(Company, on_delete=models.CASCADE, verbose_name="Empresa", null=True, blank=True)
    observations = models.TextField(blank=True, null=True, verbose_name='Observaciones')
    is_round_trip = models.BooleanField(default=False, verbose_name="Ida y Vuelta")
    price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio", default=0.00,blank=True, null=True)
    discounted_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio con Descuento", default=0, blank=True, null=True)
    final_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name="Precio Final", default=0, blank=True, null=True)
    discount_coupon = models.ForeignKey(DiscountCoupon, on_delete=models.SET_NULL, null=True, blank=True, verbose_name="Cupón de Descuento")
    comprobante = models.ImageField(upload_to='comprobantes/', blank=True, null=True, verbose_name="Comprobante del Viaje")
    paid = models.BooleanField(default=False, verbose_name="Pagado", blank=True, null=True)
    paid_driver = models.BooleanField(default=False, verbose_name="Pagado", blank=True, null=True)

    def apply_discount(self):
        if self.discount_coupon and self.discount_coupon.is_valid():
            # Verificar que la empresa del cupón coincida con la empresa de la orden
            if self.discount_coupon.company != self.company:
                return self.rate.price  # Retornar el precio original si la empresa no coincide

            if self.discount_coupon.discount_type == 'percentage':
                discount_amount = self.rate.price * (self.discount_coupon.discount_value / 100)
            else:
                discount_amount = self.discount_coupon.discount_value

            return max(self.rate.price - discount_amount, 0)
        return self.rate.price

    def enviar_id_a_usuario(self):
        CustomUser = get_user_model()
        conductor = CustomUser.objects.get(pk=self.user_driver.user.pk)
        if conductor:
            serialized_transfer = serialize("json", [self], use_natural_foreign_keys=True)
            serialized_transfer_data = json.loads(serialized_transfer)[0]  # Convertir a dict

            # Obtener el nombre y apellido del usuario
            user = self.service_requested
            try:
                user_full_name = f"{user.first_name} {user.last_name}"
            except:
                user_full_name = "Usuario invitado"

            # Obtener la URL completa de la imagen de la empresa
            if user.company and user.company.image:
                company_image_url = user.company.image.url
            else:
                company_image_url = ""

            # Obtener la información completa de las personas a trasladar
            persons_to_transfer = list(self.person_to_transfer.values('name', 'phone', 'company'))

            # Añadir el nombre y apellido, la URL de la imagen de la empresa y la información de las personas a trasladar al diccionario de la transferencia
            serialized_transfer_data['fields']['service_requested'] = user_full_name
            serialized_transfer_data['fields']['company_image_url'] = company_image_url
            serialized_transfer_data['fields']['person_to_transfer'] = persons_to_transfer

            # Serializar los desvíos
            serialized_deviations = serialize("json", self.deviation.all(), use_natural_foreign_keys=True)
            serialized_deviations_data = json.loads(serialized_deviations)

            # Añadir los desvíos al diccionario de la transferencia
            serialized_transfer_data['fields']['deviations'] = serialized_deviations_data
            serialized_transfer_data['fields']['id'] = self.id

            if self.is_round_trip:
                rates = {
                    "driver_gain": str(self.rate.driver_price_round_trip)
                }
            else:
                rates = {
                    "driver_gain": str(self.rate.driver_price)
                }

            channel_layer = get_channel_layer()
            async_to_sync(channel_layer.group_send)(
                conductor.username,
                {
                    "type": "transferencia_validada",
                    "transferencia_id": self.id,
                    "transferencia_data": json.dumps(serialized_transfer_data),  # Convertir de nuevo a JSON
                    "rates": rates
                },
            )
            print(serialized_transfer_data)
            print(persons_to_transfer)
    
    def save(self, *args, **kwargs):
        # obtener compañía del service_requested y asignarla a la solicitud
        try:
            self.company = self.service_requested.company
        except:
            self.company = None

        # try:
        #     self.company = self.service_requested.company.name
        # except: 
        #     self.company = None
        # Validación personalizada antes de guardar
        if self.status == 'aprobada':
            # Realiza la funcionalidad adicional que necesitas
            if self.user_driver:
                print("Se ha seleccionado conductor")
                self.enviar_id_a_usuario()
            else:
                print("No se selecciono conductor")
        if not self.pk:
            super().save(*args, **kwargs)

        # self.apply_discount()
        self.final_price = self.price + (self.deviation.all().count() * self.rate.detour_local)

        # Llama al método save original para guardar normalmente
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Solicitud de Transferencia {self.id}"
    
    class Meta:
        verbose_name = 'Solicitud de traslado'
        verbose_name_plural = 'Solicitudes de traslado'
        ordering = ["-date_created"]