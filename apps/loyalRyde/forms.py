from django.forms import *
from .models import *

class TransferRequestForm(ModelForm):
    class Meta:
        model = TransferRequest
        fields = '__all__'
