from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, 
                                ListView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *

#  Agregar Destino
class ArrivalPointCreateView(LoginRequiredMixin, CreateView):
    model = ArrivalPoint
    form_class = AddArrivalForm
    # fields = '__all__'
    template_name = 'loyal_ryde_system/add.html'
    success_url = reverse_lazy('core:rates_arrival_list')

    def get_context_data(self,**kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Registrar Destino"
        context['url_return'] = self.success_url
        return context

# Actualizar Destino
class ArrivalPointUpdateView(LoginRequiredMixin, UpdateView):
    model = ArrivalPoint
    form_class = AddArrivalForm
    template_name = 'loyal_ryde_system/add.html'
    success_url = reverse_lazy('core:rates_arrival_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Actualizar Destino"
        context['url_return'] = self.success_url
        return context

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Destino actualizado exitosamente!')
        return response

# Eliminar Destino
class ArrivalPointDeleteView(LoginRequiredMixin, DeleteView):
    model = ArrivalPoint
    template_name = 'loyal_ryde_system/delete_arrival.html'
    success_url = reverse_lazy('core:rates_arrival_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Destino eliminada exitosamente!')
        return response
    
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Destino"
        context['text'] = "¿Está seguro de eliminar este destino?"
        context['url_cancel'] = reverse_lazy('core:rates_arrival_list')
        return context

#  Listado de Salidas
class ArrivalListView(LoginRequiredMixin, ListView):
    model = ArrivalPoint
    context_object_name = 'arrival'
    template_name = 'loyal_ryde_system/arrival_list.html'



