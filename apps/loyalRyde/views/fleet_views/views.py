
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, ListView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *

#  Agregar Flota
class FleetAdd(LoginRequiredMixin, CreateView):
    model = Fleet
    form_class = AddFleetForm
    template_name = 'loyal_ryde_system/add_fleet.html'
    success_url = reverse_lazy('core:fleet_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


#  Agregar Tipo de flota
class FleetTypeAdd(LoginRequiredMixin, CreateView):
    model = FleetType
    form_class = AddFleetTypeForm
    template_name = 'loyal_ryde_system/add_fleet_type.html'
    success_url = reverse_lazy('core:fleet_list_type')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


class FleetTypeUpdateView(LoginRequiredMixin, UpdateView):
    model = FleetType
    form_class = AddFleetTypeForm
    template_name = 'loyal_ryde_system/add_fleet_type.html'  # Reutiliza el mismo template
    success_url = reverse_lazy('core:fleet_list_type')

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context

#  Listado de Flotas
class FleetListView(LoginRequiredMixin, ListView):
    model = Fleet
    context_object_name = 'fleets'
    template_name = 'loyal_ryde_system/fleet_list.html'

#  Listado de Flotas
class FleeTypetListView(LoginRequiredMixin, ListView):
    model = FleetType
    context_object_name = 'fleets'
    template_name = 'loyal_ryde_system/fleet_list_type.html'
