
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import (ListView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *


#  Listado de Viajes en progreso
class TripsProgressListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_progress.html'

    def get_queryset(self):
        return TransferRequest.objects.filter(status='en proceso')

#  Listado de Viajes en completados
class TripsCompletedListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_complete.html'
    
    def get_queryset(self):
        return TransferRequest.objects.filter(status='finalizada')

#  Listado de Viajes en en espera
class TripsHoldListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_on_hold.html'
    
    def get_queryset(self):
        return TransferRequest.objects.filter(status__in=['esperando validación', 'validada'])


#  Listado de Viajes en en espera
class TripsAroveListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_approve.html'
    
    def get_queryset(self):
        return TransferRequest.objects.filter(status='aprobada')

#  Listado de Viajes programados
class TripsProgramedListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_programed.html'
    
    def get_queryset(self):
        return TransferRequest.objects.filter(status='validada')

#  Listado de Viajes cancelados
class TripsCancelledListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    context_object_name = 'transfer'
    template_name = 'loyal_ryde_system/trips/trips_canceled.html'
    
    def get_queryset(self):
        return TransferRequest.objects.filter(status='cancelada')


