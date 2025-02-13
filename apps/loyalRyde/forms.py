from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from django.utils.crypto import get_random_string
from django.core.mail import send_mail, EmailMessage
from .models import *

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
            else:
                form.field.widget.attrs['class'] = 'form-control'

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
            # agregar al campo observations que es textarea solo 2 filas de altura
            'observations': Textarea(attrs={'class': 'form-control', 'rows': 2}),
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

    def __init__(self,*args,**kwargs):
        super().__init__(*args,**kwargs)
        for form in  self.visible_fields():
            if form.name == 'role' or form.name == 'company' or form.name == 'status':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            elif form.name == 'travel_approval':
                pass
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'
    
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
            if form.name == 'route' or form.name== 'type_vehicle':
                form.field.widget.attrs['class'] = 'form-select mb-2'
                form.field.widget.attrs['data-control'] = 'select2'
                form.field.widget.attrs['data-hide-search'] = 'true'
            else:
                form.field.widget.attrs['class'] = 'form-control mb-2'

    class Meta:
        model = Rates
        fields = '__all__'

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
        fields = '__all__'

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