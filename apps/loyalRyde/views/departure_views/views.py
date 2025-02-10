

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *

#  Agregar Salida
class DeparturePointCreateView(LoginRequiredMixin, CreateView):
    model = DeparturePoint
    form_class = AddDepartureForm
    template_name = 'loyal_ryde_system/add.html'
    success_url = reverse_lazy('core:rates_departure_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Registrar Salida"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Salida registrada exitosamente!')
        return response

# Actualizar Salida
class DepartureUpdateView(LoginRequiredMixin, UpdateView):
    model = DeparturePoint
    form_class = AddDepartureForm
    template_name = 'loyal_ryde_system/add.html'
    success_url = reverse_lazy('core:rates_departure_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Actualizar Salida"
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Salida actualizada exitosamente!')
        return response

# Eliminar Salida
class DepartureDeleteView(LoginRequiredMixin, DeleteView):
    model = DeparturePoint
    template_name = 'loyal_ryde_system/delete_departure.html'
    success_url = reverse_lazy('core:rates_departure_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Salida eliminada exitosamente!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Salida"
        context['text'] = "¿Está seguro de eliminar esta salida?"
        context['url_cancel'] = reverse_lazy('core:rates_departure_list')
        return context

#  Listado de Destinos
class DepartureListView(LoginRequiredMixin, ListView):
    model = DeparturePoint
    context_object_name = 'departure'
    template_name = 'loyal_ryde_system/departure_list.html'
