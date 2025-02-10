

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, DeleteView, ListView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *


#  Agregar Ruta
class RouteCreateView(LoginRequiredMixin, CreateView):
    model = Route
    form_class = AddRouteForm
    template_name = 'loyal_ryde_system/add_route.html'
    success_url = reverse_lazy('core:route_list')

#  Agregar Ruta
class RouteUpdate(LoginRequiredMixin, UpdateView):
    model = Route
    form_class = AddRouteForm
    template_name = 'loyal_ryde_system/add_route.html'
    success_url = reverse_lazy('core:route_list')

class RouteDeleteView(LoginRequiredMixin, DeleteView):
    model = Route
    template_name = 'loyal_ryde_system/delete_departure.html'
    success_url = reverse_lazy('core:route_list')
    
    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Ruta eliminada exitosamente!')
        return response

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = "Eliminar Ruta"
        context['text'] = "¿Está seguro de eliminar esta Ruta?"
        context['url_cancel'] = reverse_lazy('core:route_list')
        return context

#  Listado de Rutas
class RouteListView(LoginRequiredMixin, ListView):
    model = Route
    context_object_name = 'routes'
    template_name = 'loyal_ryde_system/route_list.html'



