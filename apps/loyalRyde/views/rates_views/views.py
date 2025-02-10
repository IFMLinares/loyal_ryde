
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *


#  Agregar tarifas
class RatesCreateView(LoginRequiredMixin, CreateView):
    model = Rates
    form_class = AddRateForm
    template_name = 'loyal_ryde_system/add_rate.html'
    success_url = reverse_lazy('core:rates_list')

#  Agregar tarifas
class RatesUpdateView(LoginRequiredMixin, UpdateView):
    model = Rates
    form_class = AddRateForm
    template_name = 'loyal_ryde_system/add_rate.html'
    success_url = reverse_lazy('core:rates_list')

class RatesDeleteView(LoginRequiredMixin, DeleteView):
    model = Rates
    template_name = 'loyal_ryde_system/delete_departure.html'
    success_url = reverse_lazy('core:rates_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tarifa eliminada exitosamente!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Tarifa"
        context['text'] = "¿Está seguro de eliminar esta tarifa?"
        context['url_cancel'] = reverse_lazy('core:rates_list')
        return context

#  Listado de Tarifas
class RatesListView(LoginRequiredMixin, ListView):
    model = Rates
    context_object_name = 'rates'
    template_name = 'loyal_ryde_system/rates.html'


