from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from apps.loyalRyde.forms import AddZoneRateForm
from apps.loyalRyde.models_zones import ZoneRate


class ZoneRatesCreateView(LoginRequiredMixin, CreateView):
    model = ZoneRate
    form_class = AddZoneRateForm
    template_name = 'loyal_ryde_system/add_zone_rate.html'
    success_url = reverse_lazy('core:zone_rates_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


class ZoneRatesUpdateView(LoginRequiredMixin, UpdateView):
    model = ZoneRate
    form_class = AddZoneRateForm
    template_name = 'loyal_ryde_system/add_zone_rate.html'
    success_url = reverse_lazy('core:zone_rates_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['url_return'] = self.success_url
        return context


class ZoneRatesDeleteView(LoginRequiredMixin, DeleteView):
    model = ZoneRate
    template_name = 'loyal_ryde_system/delete_departure.html'
    success_url = reverse_lazy('core:zone_rates_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Tarifa de zona eliminada exitosamente!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Tarifa de Zona"
        context['text'] = "¿Está seguro de eliminar esta tarifa de zona?"
        context['url_cancel'] = reverse_lazy('core:zone_rates_list')
        return context


class ZoneRatesListView(LoginRequiredMixin, ListView):
    model = ZoneRate
    context_object_name = 'zone_rates'
    template_name = 'loyal_ryde_system/zone_rates.html'
