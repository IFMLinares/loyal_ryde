import calendar
import json

from django.contrib.auth.mixins import LoginRequiredMixin
from django.core import serializers
from django.core.mail import EmailMultiAlternatives
from django.contrib import messages

from django.db.models import Count, Sum
from django.db.models.functions import TruncMonth
from django.http import JsonResponse
from django.template.loader import render_to_string
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils import timezone
from django.views.decorators.csrf import csrf_exempt
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.views.generic import (TemplateView)
from django.shortcuts import redirect, get_object_or_404

from django.core.mail import send_mail

from .forms import *
from .models import *
# Create your views here.

#  INICIO
class Index(LoginRequiredMixin, TemplateView):
    template_name = 'loyal_ryde_system/index/index.html'

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
        company_id = request.POST.get('company')

        # Validar si el company_id es un número o "N/A"
        if company_id == "N/A":
            company = None
        else:
            try:
                company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                return JsonResponse({'error': 'La empresa no existe.'}, status=400)


        # Verificar si ya existe un registro con los datos proporcionados
        person = PeopleTransfer.objects.filter(name=name, phone=phone, company=company).first()
        if person:
            data = serializers.serialize('json', [person])
            return JsonResponse({'people_transfer': data}, status=200)

        # Crear un nuevo registro si no existe
        person = PeopleTransfer.objects.create(name=name, phone=phone, company=company)
        data = serializers.serialize('json', [person])
        return JsonResponse({'people_transfer': data}, status=200)

@csrf_exempt
def approve_request(request):
    if request.method == 'POST':
        print(request.user.role)
        # Permitir solo a administradores o supervisores aprobar solicitudes
        if request.user.role not in ['administrador', 'supervisor']:
            return JsonResponse({'status': 'error', 'message': 'No tiene permisos para aprobar esta solicitud.'})


        request_id = request.POST.get('request_id')
        transfer_request = TransferRequest.objects.get(id=request_id)

        if transfer_request.service_requested.company != request.user.company:
            return JsonResponse({'status': 'error', 'message': 'No puede aprobar solicitudes de otra compañía.'})

        transfer_request.status = 'validada'
        transfer_request.approved_by = request.user
        transfer_request.save()
        return JsonResponse({'status': 'success', 'message': 'La solicitud ha sido validada con éxito.'})

def send_approval_email(transfer_request):
    # Obtener los correos de los administradores
    admin_emails = CustomUser.objects.filter(role='administrador').values_list('email', flat=True)
    company_emails = CustomUser.objects.filter(company=transfer_request.company).values_list('email', flat=True)
    driver_email = transfer_request.user_driver.user.email if transfer_request.user_driver else None

    recipients = set(admin_emails) | set(company_emails)
    if driver_email:
        recipients.add(driver_email)

    # Obtener datos adicionales
    print(transfer_request)
    passengers = transfer_request.person_to_transfer.all()
    deviations = transfer_request.deviation.all()


    # Crear el asunto y el mensaje del correo
    subject = f"Solicitud de traslado aprobada (ID: {transfer_request.id})"
    html_message = render_to_string('emails/approve_transfer.html', {
        'transfer_request': transfer_request,
        'passengers': passengers,
        'deviations': deviations,
        'message': 'La solicitud de traslado ha sido aprobada.',
    })
    plain_message = strip_tags(html_message)
    from_email = 'loyalride.test@gmail.com'

    # Enviar el correo
    send_mail(subject, plain_message, from_email, list(recipients), html_message=html_message)

@csrf_exempt
def approve_request_admin(request):
    if request.method == 'POST':
        if request.user.role != 'administrador':
            return JsonResponse({'status': 'error', 'message': 'No tiene permisos para aprobar esta solicitud.'})

        request_id = request.POST.get('request_id')
        transfer_request = TransferRequest.objects.get(id=request_id)

        if not transfer_request.user_driver:
            return JsonResponse({'status': 'error', 'message': 'No ha seleccionado un conductor.'})
        else:
            transfer_request.status = 'aprobada'
            transfer_request.save()

            # Enviar notificación por correo
            send_approval_email(transfer_request)

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
        departure_state = request.GET.get("departure_state")
        departure_sector = request.GET.get("departure_sector", "")
        arrival_city = request.GET.get("arrival_city")
        arrival_state = request.GET.get("arrival_state")
        arrival_sector = request.GET.get("arrival_sector", "")
        nro = request.GET.get("nro")
        print(departure_city, departure_state, arrival_city, arrival_state)

        # Validar que todos los parámetros estén presentes y no sean None o vacíos
        if not all([departure_city, departure_state, arrival_city, arrival_state, nro]):
            return JsonResponse({"error": "Faltan parámetros requeridos para buscar la tarifa."}, status=400)

        try:
            nro = int(nro)
            # Estrategia de resolución de ruta (más específico primero):
            # 1) Si hay sector de llegada, intentar por sector+estado
            # 2) Si no, intentar por ciudad+estado (como antes)

            route = None

            # Intento 1: sector de llegada específico (prefiere coincidencia exacta primero)
            if arrival_sector:
                route_qs = Route.objects.filter(
                    departure_point__name__icontains=departure_city,
                    departure_point__state__icontains=departure_state,
                    arrival_point__state__icontains=arrival_state,
                )
                # exacto por sector
                route = route_qs.filter(arrival_point__name__iexact=arrival_sector).first()
                # si no, icontains por sector
                if route is None:
                    route = route_qs.filter(arrival_point__name__icontains=arrival_sector).first()

            # Intento 2: fallback a ciudad si no se encontró por sector
            if route is None:
                route = Route.objects.filter(
                    departure_point__name__icontains=departure_city,
                    departure_point__state__icontains=departure_state,
                    arrival_point__name__icontains=arrival_city,
                    arrival_point__state__icontains=arrival_state,
                ).first()

            if route is None:
                raise Route.DoesNotExist()
            # Luego, busca la tarifa asociada a esa ruta
            rate = Rates.objects.filter(route=route)
            rate_data = []
            for n in rate:
                rate_data.append({
                    "rate_id": n.id,
                    'rate_vehicle': f'{n.type_vehicle}',
                    'rate_route': f'{n.route.departure_point}-{n.route.arrival_point}',
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
                    'rate_service_type': n.service_type if n.service_type else 'No disponible',
                })
                print(rate_data)
            response_data = {
                "rates": rate_data
            }
            return JsonResponse(response_data)
        except (Route.DoesNotExist, Rates.DoesNotExist, ValueError):
            return JsonResponse({"error": "No se encontró una tarifa para esta ruta o los parámetros son inválidos."}, status=404)

@csrf_exempt
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


def toggle_paid_driver(request, pk):
    transfer = get_object_or_404(TransferRequest, pk=pk)
    transfer.paid_driver = not transfer.paid_driver
    transfer.save()
    if transfer.paid_driver:
        messages.success(request, "¡El viaje fue marcado como pagado al conductor!")
    else:
        messages.success(request, "¡El viaje fue marcado como NO pagado al conductor!")
    return redirect(request.META.get('HTTP_REFERER', '/'))


@csrf_exempt
def get_whatsapp_link(request):
    if request.method == 'POST':
        transfer_id = request.POST.get('transfer_id')
        try:
            transfer = TransferRequest.objects.get(id=transfer_id)
            driver = transfer.user_driver
            phone = driver.user.phone
            # Normaliza el número (quita espacios, guiones, etc)
            phone = ''.join(filter(str.isdigit, phone))
            if phone.startswith('0'):
                phone = phone[1:]
            whatsapp_number = f"58{phone}"

            # Construye el mensaje
            persons = ', '.join([f"{p.name} ({p.phone})" for p in transfer.person_to_transfer.all()])
            deviations = ', '.join([d.desviation_direc for d in transfer.deviation.all()])
            empresa = transfer.company.name if transfer.company else "Modo invitado"
            # Generar id codificado en base64
            import base64
            encoded_id = base64.b64encode(str(transfer.id).encode()).decode()
            # Construir enlaces
            url_base = request.build_absolute_uri('/')[:-1]  # Quita el slash final
            iniciar_url = f"{url_base}/transfer/start/?id={encoded_id}"
            finalizar_url = f"{url_base}/transfer/finish/?id={encoded_id}"

            mensaje = (
                f"Solicitud de traslado aprobada\n"
                f"ID: {transfer.id}\n"
                f"Conductor: {driver.user.get_full_name()}\n"
                f"Pasajero(s): {persons}\n"
                f"Salida: {transfer.destination_direc}\n"
                f"Destino: {transfer.departure_direc}\n"
                f"Desvíos: {deviations if deviations else 'Sin desvíos'}\n"
                f"Fecha: {transfer.date}\n"
                f"Hora: {transfer.hour}\n"
                f"Empresa solicitante: {empresa}\n"
                f"Estado: {transfer.status}\n"
                f"Iniciar traslado: \n{iniciar_url}\n"
                f"Finalizar traslado: \n{finalizar_url}\n"
            )
            # Codifica el mensaje para URL
            from urllib.parse import quote
            mensaje_url = quote(mensaje)
            whatsapp_url = f"https://wa.me/{whatsapp_number}?text={mensaje_url}"

            return JsonResponse({'status': 'success', 'whatsapp_url': whatsapp_url})
        except TransferRequest.DoesNotExist:
            return JsonResponse({'status': 'error', 'message': 'Transferencia no encontrada.'})
    return JsonResponse({'status': 'error', 'message': 'Método no permitido.'})
