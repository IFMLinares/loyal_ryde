from django.forms import *
from django.contrib.auth.forms import UserCreationForm
from .models import *

class TransferRequestForm(ModelForm):
    class Meta:
        model = TransferRequest
        fields = '__all__'

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
        fields = UserCreationForm.Meta.fields + ('first_name', 'last_name', 'email' ,'phone', 'role', 'department', 'status','company', 'travel_approval')
        
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
            if form.name == 'route' or form.name== 'vehicle':
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
            )
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