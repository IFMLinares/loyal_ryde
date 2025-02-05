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

from .forms import *
from .models import *
# Create your views here.

#  INICIO
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        now = timezone.now()
        start_of_month = now.replace(day=1)
        context['latest_transfer_requests'] = TransferRequest.objects.all().order_by('-date_created')[:10]
        context['in_progress_transfer_requests'] = TransferRequest.objects.filter(status='en proceso').order_by('-date_created')[:10]
        context['total_transfer_requests'] = TransferRequest.objects.count()
        context['total_records'] = TransferRequest.objects.filter(date_created__gte=start_of_month).count()
        return context

class GeneralReportsView(TemplateView):
    template_name = 'loyal_ryde_system/reportes_generales.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        company_name = self.request.GET.get('company_name', 'Todas')

        transfer_requests = TransferRequest.objects.all()
        if start_date and end_date:
            transfer_requests = transfer_requests.filter(date__range=[start_date, end_date])
        if company_name and company_name != 'Todas':
            transfer_requests = transfer_requests.filter(company=company_name)

        transfer_requests = list(transfer_requests.values('status').annotate(count=Count('status')))
        context['transfer_requests_json'] = json.dumps(transfer_requests)
        context['companies'] = Company.objects.all()
        context['selected_company'] = company_name
        return context

    def get(self, request, *args, **kwargs):
        if request.headers.get('x-requested-with') == 'XMLHttpRequest':
            start_date = request.GET.get('start_date')
            end_date = request.GET.get('end_date')
            company_name = request.GET.get('company_name', 'Todas')

            transfer_requests = TransferRequest.objects.all()
            if start_date and end_date:
                transfer_requests = transfer_requests.filter(date__range=[start_date, end_date])
            if company_name and company_name != 'Todas':
                transfer_requests = transfer_requests.filter(company=company_name)

            transfer_requests = list(transfer_requests.values('status').annotate(count=Count('status')))
            return JsonResponse({'transfer_requests_json': json.dumps(transfer_requests)})
        return super().get(request, *args, **kwargs)

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

@csrf_exempt
def approve_request_admin(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        transfer_request = TransferRequest.objects.get(id=request_id)
        if(not transfer_request.user_driver):
            return JsonResponse({'status': 'error', 'message': 'No ha seleccionado un conductor.'})
        else:
            transfer_request.status = 'aprobada'
            transfer_request.save()
            return JsonResponse({'status': 'success', 'message': 'La solicitud ha sido aprobada con éxito.'})

@csrf_exempt
def cancel_request(request):
    if request.method == 'POST':
        request_id = request.POST.get('request_id')
        transfer_request = TransferRequest.objects.get(id=request_id)
        transfer_request.status = 'cancelada'
        transfer_request.save()
        return JsonResponse({'status': 'warning', 'message': 'La solicitud ha sido cancelada.'})


def get_company_image(request):
    company_id = request.GET.get('company_id')
    company = Company.objects.get(id=company_id)
    image_url = company.image.url  # Asumiendo que tu modelo Company tiene un campo de imagen
    return JsonResponse({'image_url': image_url})

def get_routes_by_departure(request):
    if request.method == "GET":
        departure_name = request.GET.get("departure")
        routes = Route.objects.filter(departure_point__name=departure_name)
        data = [{"id": route.id, "arrival_point": route.arrival_point.name} for route in routes]
        return JsonResponse(data, safe=False)

def get_rates(request):
    if request.method == "GET":
        departure_city = request.GET.get("departure_city")
        arrival_city = request.GET.get("arrival_city")
        print(departure_city, arrival_city)
        nro = int(request.GET.get("nro"))

        try:
            # Buscar la ruta con los nombres de las ciudades de salida y destino
            route = Route.objects.get(departure_point__name__icontains=departure_city, arrival_point__name__icontains=arrival_city)
            # Luego, busca la tarifa asociada a esa ruta
            rate = Rates.objects.filter(route=route)
            rate_data = []
            for n in rate:
                # if n.vehicle.passengers_numbers >= nro:
                rate_data.append({
                    "rate_id": n.id,
                    'rate_vehicle': f'{n.type_vehicle}',
                    'rate_route': f'{n.route.route_name}: {n.route.departure_point}-{n.route.arrival_point}',
                    'rate_price': n.price,
                    'rate_price_round_trip': n.price_round_trip,
                    'rate_driver_gain': n.driver_gain,
                    'rate_driver_price': n.driver_price,
                    'rate_driver_price_round_trip': n.driver_price_round_trip,
                    'rate_gain_loyal_ride': n.gain_loyal_ride,
                    'rate_gain_loyal_ride_round_trip': n.gain_loyal_ride_round_trip,
                    'rate_daytime_waiting_time': n.daytime_waiting_time,
                    'rate_nightly_waiting_time': n.nightly_waiting_time,
                    'rate_detour_local': n.detour_local,
                    # Agrega más campos según tus necesidades
                })
                print(rate_data)
            response_data = {
                "rates": rate_data
            }
            return JsonResponse(response_data)
        except (Route.DoesNotExist, Rates.DoesNotExist):
            return JsonResponse({"error": "No se encontró una tarifa para esta ruta."}, status=404)

@require_POST
def verify_discount_code(request):
    code = request.POST.get('code')
    try:
        coupon = DiscountCoupon.objects.get(code=code, expiration_date__gte=timezone.now())
        return JsonResponse({'valid': True, 'discount_value': str(coupon.discount_value), 'discount_type': coupon.discount_type})
    except DiscountCoupon.DoesNotExist:
        return JsonResponse({'valid': False, 'message': 'Código de descuento no válido o expirado.'})

# Email fuinctions

def send_styled_email(user, password):
    subject = 'Credenciales del sistema loyal Ride'
    html_content = render_to_string('account/email/email_send.html', {'user': user, 'login': reverse_lazy('core:index'), 'pass': password})
    text_content = strip_tags(html_content)  # Elimina las etiquetas HTML para el contenido de texto plano

    email = EmailMultiAlternatives(subject, text_content, 'loyalride.test@gmail.com', [user.email])
    email.attach_alternative(html_content, 'text/html')  # Adjunta el contenido HTML
    email.send()

def transfer_requests_per_month(request):
    # Obtener los datos de la consulta
    data = TransferRequest.objects.annotate(month=TruncMonth('date_created')).values('month').annotate(count=Count('id')).order_by('month')
    
    # Crear un diccionario con todos los meses y valores iniciales de cero
    response_data = {month: 0 for month in calendar.month_name if month}
    
    # Actualizar el diccionario con los datos de la consulta
    for item in data:
        response_data[item['month'].strftime('%B')] = item['count']
    
    return JsonResponse(response_data)


@csrf_exempt
def delete_coupon(request):
    if request.method == 'POST':
        coupon_id = request.POST.get('coupon_id')
        try:
            coupon = DiscountCoupon.objects.get(id=coupon_id)
            coupon.delete()
            return JsonResponse({'status': 'success', 'message': 'El cupón ha sido eliminado.'})
        except DiscountCoupon.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'El cupón no existe.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})

