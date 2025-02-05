import calendar
import locale
import json
from babel.dates import format_date
from datetime import datetime
from io import BytesIO

import pandas as pd
from openpyxl import Workbook
from openpyxl.cell.cell import MergedCell
from openpyxl.drawing.image import Image
from openpyxl.styles import Font, Alignment, Border, Side
from openpyxl.utils import get_column_letter

from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.contrib.auth.models import AnonymousUser, Group, User
from django.core import serializers
from django.core.mail import EmailMessage, EmailMultiAlternatives, send_mail
from django.db.models import Count, F, Q, Sum
from django.db.models.functions import TruncMonth
from django.http import HttpResponse, HttpResponseRedirect, JsonResponse
from django.shortcuts import get_object_or_404, render
from django.template.loader import render_to_string
from django.urls import reverse_lazy, reverse
from django.utils import timezone
from django.utils.crypto import get_random_string
from django.utils.dateparse import parse_date
from django.utils.html import strip_tags
from django.utils import timezone
from django.utils.timezone import now
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.views.generic import (CreateView, DeleteView, DetailView, 
                                ListView,TemplateView, UpdateView, View)

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
