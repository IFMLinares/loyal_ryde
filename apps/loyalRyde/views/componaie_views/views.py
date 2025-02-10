import calendar
import locale
import json


from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (CreateView, ListView,TemplateView, UpdateView)

from apps.loyalRyde.forms import *
from apps.loyalRyde.models import *

# listado de Empresas
class CompaniesListView(LoginRequiredMixin, ListView):
    model = Company
    template_name = 'loyal_ryde_system/companies_list.html'
    context_object_name = 'companies'

#  Agregar Empresa
class CompnayAdd(LoginRequiredMixin, CreateView):
    model = Company
    form_class = AddCompanyForm
    success_url =  reverse_lazy('core:companies_list')
    template_name = 'loyal_ryde_system/add_company.html'

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Formulario guardado exitosamente!')
        return response

class CompanyUpdateView(LoginRequiredMixin, UpdateView):
    model = Company
    form_class = AddCompanyForm
    template_name = 'loyal_ryde_system/update_company.html'
    success_url = reverse_lazy('core:companies_list')

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, 'Registro actualizado exitosamente!')
        return response

class CompanyFilteredTransferRequestsView(LoginRequiredMixin, UserPassesTestMixin, TemplateView):
    template_name = 'loyal_ryde_system/company_filtered_transfer_requests.html'

    def test_func(self):
        return self.request.user.role in ['supervisor', 'operator']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        user_company = self.request.user.company
        transfer_requests = TransferRequest.objects.filter(company=user_company)
        context['transfer_requests'] = transfer_requests
        return context
