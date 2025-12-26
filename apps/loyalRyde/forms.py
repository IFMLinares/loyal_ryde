from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, EmailMessage
from .models import *
from .models_zones import Zone

class TransferRequestForm(ModelForm):
    discount_code = CharField(required=False, widget=TextInput(attrs={'class': 'form-control', 'placeholder': 'Código de Descuento'}))

    def clean_discount_code(self):
        code = self.cleaned_data.get('discount_code')
        if code:
            try:
                coupon = DiscountCoupon.objects.get(code=code)
                if coupon.expiration_date < timezone.now().date():
                    raise ValidationError("El cupón ha expirado.")
                if coupon.company != self.cleaned_data.get('company'):
                    raise ValidationError("El cupón no es válido para su empresa.")
                if coupon.usage_limit <= 0:
                    raise ValidationError("El cupón ha alcanzado su límite de uso.")
                return coupon
            except DiscountCoupon.DoesNotExist:
                raise ValidationError("El cupón no es válido.")
        return None

    def exclude_user_driver(self, user):
        if user and user.role in ['supervisor', 'operator']:
            self.fields.pop('user_driver')

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if form.name == 'executive_transfer' or form.name == 'encomienda' or form.name == 'driver' or form.name == 'id_fly_checkbox' or form.name == 'is_round_trip':
                form.field.widget.attrs['class'] = 'form-check-input'
            elif form.name == 'person_to_transfer':
                form.field.widget.attrs['class'] = 'form-select'
            elif form.name == 'user_driver' or form.name == 'payment_method':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                # form.field.widget.attrs['data-hide-search'] = 'true'
            elif form.name == 'company':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
            else:
                form.field.widget.attrs['class'] = 'form-control'
        


        if self.instance.pk:
            selected_people = self.instance.person_to_transfer.all()
            self.fields['person_to_transfer'].queryset = selected_people


    class Meta:
        model = TransferRequest
        fields = '__all__'
        widgets = {
            'executive_transfer': CheckboxInput(),
            'encomienda': CheckboxInput(),
            'driver': CheckboxInput(),
            'is_round_trip': CheckboxInput(),
            'id_fly_checkbox': CheckboxInput(),
            'person_to_transfer': SelectMultiple(),
            'rate': Select(attrs={'class': 'form-control'}),
            'zone_rate': HiddenInput(),
            # agregar al campo observations que es textarea solo 2 filas de altura
            'observations': Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'company': Select(attrs={'class': 'form-select mb-2', 'data-control': 'select2'}),
            # 'destination_direc': TextInput(attrs={'autocomplete': 'off'}),
            # 'departure_direc': TextInput(attrs={'autocomplete': 'off'})
        }

class AddCompanyForm(ModelForm):

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if form.name != 'image':
                form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = Company
        fields = ['name', 'rif', 'address', 'phone', 'email', 'image']
        widgets = {
            'name': TextInput(
                attrs={
                    'class' : 'form-control mb-2',
                },
            ),
        }

class CustomUserCreationForm(UserCreationForm):

    ci = CharField(
        required=False,
        label="Cédula de Identidad",
        widget=TextInput(attrs={'class': 'form-control mb-2'})
    )

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if self.instance and self.instance.pk:
                try:
                    driver = CustomUserDriver.objects.get(user=self.instance)
                    self.fields['ci'].initial = driver.ci
                except CustomUserDriver.DoesNotExist:
                    pass
            if form.name == 'username' and self.instance and self.instance.pk:
                form.field.widget.attrs['readonly'] = True
            if form.name == 'role' or form.name == 'company' or form.name == 'status':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            elif form.name == 'travel_approval':
                pass
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'
    
    def clean_username(self):
        # Si es edición, no permitir cambiar el username y no validar duplicado contra sí mismo
        if self.instance and self.instance.pk:
            return self.instance.username
        return self.cleaned_data['username']

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        exclude = ['password1','password2']
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email', 'phone', 'role', 'department', 'status', 'company', 'travel_approval')
        widgets = {
            'role': Select(
                attrs={
                    'data-placeholder': "seleccione un estatus de usuario",
                },
            ),
            'status': Select(
                attrs={
                    'data-placeholder': "Seleccione un rol de usuario",
                },
            ),
            'company': Select(
                attrs={
                    'data-placeholder': "Seleccione la empresa",
                },
            ),
            'destination_direc': TextInput(
                attrs={
                    'autocomplete': 'off',
                },
            ),
            'destination_landmark': TextInput(
                attrs={
                    'autocomplete': 'off',
                },
            ),
        }

class CustomUserUpdateForm(ModelForm):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            if form.name == 'role' or form.name == 'company' or form.name == 'status':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            elif form.name == 'travel_approval':
                pass
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = CustomUser
        fields = ('first_name', 'last_name', 'email', 'phone', 'role', 'department', 'status', 'company', 'travel_approval')
        widgets = {
            'role': Select(
                attrs={
                    'data-placeholder': "seleccione un estatus de usuario",
                },
            ),
            'status': Select(
                attrs={
                    'data-placeholder': "Seleccione un rol de usuario",
                },
            ),
            'company': Select(
                attrs={
                    'data-placeholder': "Seleccione la empresa",
                },
            ),
            'destination_direc': TextInput(
                attrs={
                    'autocomplete': 'off',
                },
            ),
            'destination_landmark': TextInput(
                attrs={
                    'autocomplete': 'off',
                },
            ),
        }

class AddRouteForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if form.name == 'departure_point' or form.name == 'arrival_point':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = Route
        fields = ['route_name', 'departure_point','arrival_point',]

class AddRateForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if form.name == 'route' or form.name== 'type_vehicle' or form.name == 'service_type':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

        # Etiquetas y ayudas en español
        labels = {
            'service_type': 'Tipo de servicio',
            'route': 'Ruta (origen/destino)',
            'type_vehicle': 'Tipo de vehículo',
            'price': 'Precio (USD)',
            'price_round_trip': 'Precio ida y vuelta (USD)',
            'detour_local': 'Costo desvío local (USD)',
            'daytime_waiting_time': 'Hora de espera diurna (USD/h)',
            'nightly_waiting_time': 'Hora de espera nocturna (USD/h)',
            'driver_gain': 'Ganancia del conductor (%)',
            'driver_gain_waiting_time': 'Ganancia espera (%)',
            'driver_gain_detour_local': 'Ganancia desvío (%)',
            'driver_price': 'Pago al conductor (USD)',
            'driver_price_round_trip': 'Pago al conductor ida y vuelta (USD)',
            'gain_loyal_ride': 'Ganancia Loyal Ride (USD)',
            'gain_loyal_ride_round_trip': 'Ganancia Loyal Ride ida y vuelta (USD)',
            'driver_gain_detour_local_quantity': 'Ganancia desvío (USD)',
            'driver_daytime_waiting_time': 'Pago espera diurna (USD/h)',
            'driver_nightly_waiting_time': 'Pago espera nocturna (USD/h)',
        }
        helps = {
            'service_type': 'Seleccione el tipo de servicio',
            'route': 'Ruta fija configurada (origen y destino)',
            'type_vehicle': 'Tipo de vehículo para la tarifa',
            'price': 'Monto fijo a cobrar',
            'price_round_trip': 'Monto fijo ida y vuelta',
            'detour_local': 'Tarifa por desvío local',
            'daytime_waiting_time': 'Tarifa por hora de espera diurna',
            'nightly_waiting_time': 'Tarifa por hora de espera nocturna',
            'driver_gain': 'Porcentaje del precio para el conductor',
            'driver_gain_waiting_time': 'Porcentaje aplicado a esperas',
            'driver_gain_detour_local': 'Porcentaje aplicado al desvío',
            'driver_price': 'Calculado automáticamente',
            'driver_price_round_trip': 'Calculado automáticamente',
            'gain_loyal_ride': 'Calculado automáticamente',
            'gain_loyal_ride_round_trip': 'Calculado automáticamente',
            'driver_gain_detour_local_quantity': 'Calculado automáticamente',
            'driver_daytime_waiting_time': 'Calculado automáticamente',
            'driver_nightly_waiting_time': 'Calculado automáticamente',
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label
        for name, help_text in helps.items():
            if name in self.fields:
                self.fields[name].help_text = help_text

    class Meta:
        model = Rates
        fields = '__all__'
        labels = {
            'service_type': 'Tipo de servicio',
            'route': 'Ruta (origen/destino)',
            'type_vehicle': 'Tipo de vehículo',
            'price': 'Precio (USD)',
            'price_round_trip': 'Precio ida y vuelta (USD)',
            'detour_local': 'Costo desvío local (USD)',
            'daytime_waiting_time': 'Hora de espera diurna (USD/h)',
            'nightly_waiting_time': 'Hora de espera nocturna (USD/h)',
            'driver_gain': 'Ganancia del conductor (%)',
            'driver_gain_waiting_time': 'Ganancia espera (%)',
            'driver_gain_detour_local': 'Ganancia desvío (%)',
            'driver_price': 'Pago al conductor (USD)',
            'driver_price_round_trip': 'Pago al conductor ida y vuelta (USD)',
            'gain_loyal_ride': 'Ganancia Loyal Ride (USD)',
            'gain_loyal_ride_round_trip': 'Ganancia Loyal Ride ida y vuelta (USD)',
            'driver_gain_detour_local_quantity': 'Ganancia desvío (USD)',
            'driver_daytime_waiting_time': 'Pago espera diurna (USD/h)',
            'driver_nightly_waiting_time': 'Pago espera nocturna (USD/h)',
        }
        help_texts = {
            'service_type': 'Seleccione el tipo de servicio',
            'route': 'Ruta fija configurada (origen y destino)',
            'type_vehicle': 'Tipo de vehículo para la tarifa',
            'price': 'Monto fijo a cobrar',
            'price_round_trip': 'Monto fijo ida y vuelta',
            'detour_local': 'Tarifa por desvío local',
            'daytime_waiting_time': 'Tarifa por hora de espera diurna',
            'nightly_waiting_time': 'Tarifa por hora de espera nocturna',
            'driver_gain': 'Porcentaje del precio para el conductor',
            'driver_gain_waiting_time': 'Porcentaje aplicado a esperas',
            'driver_gain_detour_local': 'Porcentaje aplicado al desvío',
            'driver_price': 'Calculado automáticamente',
            'driver_price_round_trip': 'Calculado automáticamente',
            'gain_loyal_ride': 'Calculado automáticamente',
            'gain_loyal_ride_round_trip': 'Calculado automáticamente',
            'driver_gain_detour_local_quantity': 'Calculado automáticamente',
            'driver_daytime_waiting_time': 'Calculado automáticamente',
            'driver_nightly_waiting_time': 'Calculado automáticamente',
        }

        widgets = {
            'driver_price': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'driver_price_round_trip': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'gain_loyal_ride': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'gain_loyal_ride_round_trip': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'driver_gain_detour_local_quantity': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'driver_daytime_waiting_time': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            'driver_nightly_waiting_time': NumberInput(
                attrs={
                    'disabled': 'true'
                }
            ),
            # driver_daytime_waiting_time
            # driver_nightly_waiting_time
            # driver_gain_waiting_time
        }

class AddZoneRateForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in self.visible_fields():
            if form.name in ['origin','destination','type_vehicle','service_type']:
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

        # Etiquetas y ayudas en español
        labels = {
            'service_type': 'Tipo de servicio',
            'origin': 'Origen (Zona)',
            'destination': 'Destino (Zona)',
            'type_vehicle': 'Tipo de vehículo',
            'price': 'Precio (USD)',
            'price_round_trip': 'Precio ida y vuelta (USD)',
            'detour_local': 'Costo desvío local (USD)',
            'daytime_waiting_time': 'Hora de espera diurna (USD/h)',
            'nightly_waiting_time': 'Hora de espera nocturna (USD/h)',
            'driver_gain': 'Ganancia del conductor (%)',
            'driver_gain_waiting_time': 'Ganancia espera (%)',
            'driver_gain_detour_local': 'Ganancia desvío (%)',
            'driver_price': 'Pago al conductor (USD)',
            'driver_price_round_trip': 'Pago al conductor ida y vuelta (USD)',
            'gain_loyal_ride': 'Ganancia Loyal Ride (USD)',
            'gain_loyal_ride_round_trip': 'Ganancia Loyal Ride ida y vuelta (USD)',
            'driver_gain_detour_local_quantity': 'Ganancia desvío (USD)',
            'driver_daytime_waiting_time': 'Pago espera diurna (USD/h)',
            'driver_nightly_waiting_time': 'Pago espera nocturna (USD/h)',
        }
        helps = {
            'service_type': 'Seleccione el tipo de servicio',
            'origin': 'Zona de origen',
            'destination': 'Zona de destino',
            'type_vehicle': 'Tipo de vehículo para la tarifa',
            'price': 'Monto fijo a cobrar',
            'price_round_trip': 'Monto fijo ida y vuelta',
            'detour_local': 'Tarifa por desvío local',
            'daytime_waiting_time': 'Tarifa por hora de espera diurna',
            'nightly_waiting_time': 'Tarifa por hora de espera nocturna',
            'driver_gain': 'Porcentaje del precio para el conductor',
            'driver_gain_waiting_time': 'Porcentaje aplicado a esperas',
            'driver_gain_detour_local': 'Porcentaje aplicado al desvío',
            'driver_price': 'Calculado automáticamente',
            'driver_price_round_trip': 'Calculado automáticamente',
            'gain_loyal_ride': 'Calculado automáticamente',
            'gain_loyal_ride_round_trip': 'Calculado automáticamente',
            'driver_gain_detour_local_quantity': 'Calculado automáticamente',
            'driver_daytime_waiting_time': 'Calculado automáticamente',
            'driver_nightly_waiting_time': 'Calculado automáticamente',
        }
        for name, label in labels.items():
            if name in self.fields:
                self.fields[name].label = label
        for name, help_text in helps.items():
            if name in self.fields:
                self.fields[name].help_text = help_text

    class Meta:
        from .models_zones import ZoneRate
        model = ZoneRate
        fields = '__all__'
        labels = {
            'service_type': 'Tipo de servicio',
            'origin': 'Origen (Zona)',
            'destination': 'Destino (Zona)',
            'type_vehicle': 'Tipo de vehículo',
            'price': 'Precio (USD)',
            'price_round_trip': 'Precio ida y vuelta (USD)',
            'detour_local': 'Costo desvío local (USD)',
            'daytime_waiting_time': 'Hora de espera diurna (USD/h)',
            'nightly_waiting_time': 'Hora de espera nocturna (USD/h)',
            'driver_gain': 'Ganancia del conductor (%)',
            'driver_gain_waiting_time': 'Ganancia espera (%)',
            'driver_gain_detour_local': 'Ganancia desvío (%)',
            'driver_price': 'Pago al conductor (USD)',
            'driver_price_round_trip': 'Pago al conductor ida y vuelta (USD)',
            'gain_loyal_ride': 'Ganancia Loyal Ride (USD)',
            'gain_loyal_ride_round_trip': 'Ganancia Loyal Ride ida y vuelta (USD)',
            'driver_gain_detour_local_quantity': 'Ganancia desvío (USD)',
            'driver_daytime_waiting_time': 'Pago espera diurna (USD/h)',
            'driver_nightly_waiting_time': 'Pago espera nocturna (USD/h)',
        }
        help_texts = {
            'service_type': 'Seleccione el tipo de servicio',
            'origin': 'Zona de origen',
            'destination': 'Zona de destino',
            'type_vehicle': 'Tipo de vehículo para la tarifa',
            'price': 'Monto fijo a cobrar',
            'price_round_trip': 'Monto fijo ida y vuelta',
            'detour_local': 'Tarifa por desvío local',
            'daytime_waiting_time': 'Tarifa por hora de espera diurna',
            'nightly_waiting_time': 'Tarifa por hora de espera nocturna',
            'driver_gain': 'Porcentaje del precio para el conductor',
            'driver_gain_waiting_time': 'Porcentaje aplicado a esperas',
            'driver_gain_detour_local': 'Porcentaje aplicado al desvío',
            'driver_price': 'Calculado automáticamente',
            'driver_price_round_trip': 'Calculado automáticamente',
            'gain_loyal_ride': 'Calculado automáticamente',
            'gain_loyal_ride_round_trip': 'Calculado automáticamente',
            'driver_gain_detour_local_quantity': 'Calculado automáticamente',
            'driver_daytime_waiting_time': 'Calculado automáticamente',
            'driver_nightly_waiting_time': 'Calculado automáticamente',
        }
        widgets = {
            'driver_price': NumberInput(attrs={'disabled': 'true'}),
            'driver_price_round_trip': NumberInput(attrs={'disabled': 'true'}),
            'gain_loyal_ride': NumberInput(attrs={'disabled': 'true'}),
            'gain_loyal_ride_round_trip': NumberInput(attrs={'disabled': 'true'}),
            'driver_gain_detour_local_quantity': NumberInput(attrs={'disabled': 'true'}),
            'driver_daytime_waiting_time': NumberInput(attrs={'disabled': 'true'}),
            'driver_nightly_waiting_time': NumberInput(attrs={'disabled': 'true'}),
        }

class AddDepartureForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control mb-2'
    
    class Meta:
        model = DeparturePoint
        fields = '__all__'

class AddArrivalForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control mb-2'
    
    class Meta:
        model = ArrivalPoint
        fields = ['name', 'state']

class AddFleetForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = Fleet
        fields = '__all__'

class DiscountCouponForm(ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            if form.name == 'discount_type' or form.name == 'company':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = DiscountCoupon
        fields = ['code', 'discount_type', 'discount_value', 'expiration_date', 'company', 'usage_limit']

class AddFleetTypeForm(ModelForm):
    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = FleetType
        fields = '__all__'


class ZoneForm(ModelForm):
    geometry = CharField(widget=HiddenInput(), required=True)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for form in self.visible_fields():
            form.field.widget.attrs['class'] = 'form-control mb-2'
        # Ajustar select/checkbox
        if 'is_special' in self.fields:
            self.fields['is_special'].widget.attrs['class'] = 'form-check-input'

        # Etiquetas y ayudas en español
        self.fields['name'].label = 'Nombre de la zona'
        self.fields['name'].help_text = 'Nombre corto y descriptivo'
        self.fields['is_special'].label = '¿Es zona especial?'
        self.fields['is_special'].help_text = 'Marcar si aplica reglas o visibilidad especial'

    class Meta:
        model = Zone
        fields = ['name', 'is_special']