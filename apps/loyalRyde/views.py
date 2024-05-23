from datetime import datetime
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DeleteView, DetailView, CreateView
from django.contrib.auth.models import User
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from .forms import *
from .models import *
# Create your views here.

#  INICIO
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/index.html'

# VISTAS DE USUARIOS (PARA ADMINISTRADORES)

#  Agregar usuario
class UserAdd(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_user.html'

#  Agregar usuario (de las eempresas)
class UserCompanyAdd(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_user_company.html'

# Agregar nuevo traslado
class TransferRequestCreateView(LoginRequiredMixin, CreateView):
    model = TransferRequest
    template_name = 'loyal_ryde_system/transfer_rerquest.html'
    form_class = TransferRequestForm
    success_url = reverse_lazy('core:transfer_request_list')

    def form_valid(self, form):
        form.instance.service_requested = self.request.user
        messages.success(self.request, 'Formulario guardado exitosamente!')
        return super().form_valid(form)

    def post(self, request, *args, **kwargs):
        # Obtén la fecha directamente del POST
        fecha = request.POST.get('date')

        # Convierte la fecha al formato que Django espera
        fecha = datetime.strptime(fecha, '%m/%d/%Y').strftime('%Y-%m-%d')

        # Actualiza la fecha en los datos del POST
        request.POST = request.POST.copy()
        request.POST['date'] = fecha


        return super().post(request, *args, **kwargs)

#  Agregar conductor
class DriverAdd(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_driver.html'

#  Agregar Flota
class FleetAdd(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_fleet.html'

#  Agregar Ruta
class RouteCreateView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_route.html'

#  Listado de conductores
class DriverListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/driver_list.html'

#  Listado de Flotas
class FleetListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/fleet_list.html'

#  Listado de Rutas
class RouteListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/route_list.html'

#  Listado de Viajes en progreso
class TripsProgressListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/trips_progress.html'

#  Listado de Viajes en completados
class TripsCompletedListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/trips_complete.html'

#  Listado de Viajes en en espera
class TripsHoldListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/trips_on_hold.html'

#  Listado de Viajes programados
class TripsProgramedListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/trips_programed.html'

#  Listado de Viajes cancelados
class TripsCancelledListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/trips_canceled.html'


#  Listado de Tarifas
class RatesListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/rates.html'


#  Listado de conductores Activos
class DriverActiveListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/driver_list_active.html'

#  Listado de conductores Pendientes
class DriverPendingListView(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/driver_list_pending.html'

# Lista de administradores
class UserAdminListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'loyal_ryde_system/user_list_view.html'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

# Lista de despacahdores
class UserDispatchListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'loyal_ryde_system/user_list_view_dispatcher.html'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

# Lista de Operadores (Usuarios del cliente)
class UserOperatorListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'loyal_ryde_system/user_list_view_operators.html'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

# Lista de Supervisores (Usuarios del cliente)
class UserSupervisorListView(LoginRequiredMixin, ListView):
    model = User
    template_name = 'loyal_ryde_system/user_list_view_supervisors.html'

    def get_queryset(self):
        return User.objects.filter(is_staff=True)

# listado de Traslados
class TransferRequestListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    template_name = 'loyal_ryde_system/transfer_request_list.html'
    context_object_name = 'transfer_requests'

# listado de Empresas
class CompaniesListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    template_name = 'loyal_ryde_system/companies_list.html'
    context_object_name = 'transfer_requests'

#  Agregar Empresa
class CompnayAdd(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/add_company.html'


# AJAX FUNCTIONS
@csrf_exempt
def get_people_transfer(request):
    if request.method == 'POST':
        name = request.POST.get('name')
        phone = request.POST.get('phone')
        company = request.POST.get('company')

        person = PeopleTransfer.objects.create(name=name, phone=phone, company=company)
        data = serializers.serialize('json', [person])

        return JsonResponse({'people_transfer': data}, status=200)
    
@csrf_exempt
def approve_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        transfer_request = TransferRequest.objects.get(id=request_id)
        transfer_request.status = 'validada'
        transfer_request.save()
        return JsonResponse({'status': 'success', 'message': 'La solicitud ha sido validada con éxito.'})
