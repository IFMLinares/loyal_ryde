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

#  Listado de Destinos
class DepartureListView(LoginRequiredMixin, ListView):
    model = DeparturePoint
    context_object_name = 'departure'
    template_name = 'loyal_ryde_system/departure_list.html'
