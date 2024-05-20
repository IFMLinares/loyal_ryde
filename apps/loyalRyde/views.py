from datetime import datetime
from django.contrib import messages
from django.shortcuts import render
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import TemplateView, ListView, DeleteView, DetailView, CreateView
from django.urls import reverse_lazy
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.core import serializers

from .forms import *
from .models import *
# Create your views here.

class Index(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/index.html'

# CREAR NUEVA TRANSFERENCIA
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


# listado de Transferencias
class TransferRequestListView(LoginRequiredMixin, ListView):
    model = TransferRequest
    template_name = 'loyal_ryde_system/transfer_request_list.html'
    context_object_name = 'transfer_requests'

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
