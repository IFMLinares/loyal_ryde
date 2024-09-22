import json
from django.shortcuts import render
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt
from rest_framework.permissions import AllowAny

from django.core.mail import send_mail
from django.core.serializers import serialize
from django.utils.crypto import get_random_string
from rest_framework import status

from ..loyalRyde.models import CustomUser, CustomUserDriver,TransferStop, Desviation, TransferRequest, OTPCode
from .serializers import UserSerializers, CustomUserDriverSerializer,TransferStopSerializer, DesviationSerializer,TransferRequestSerializer,TransferRequestStatusUpdateSerializer

class UserView(APIView):

    def post(self, request, format=None):
        print("Creando usuario")
        
        user_data = request.data
        print(request.data)
        user_serializer = UserSerializers(data=user_data)
        if user_serializer.is_valid(raise_exception=False):
            user_serializer.save()
            return Response({"user": user_serializer.data}, status=200)
        return Response("MSG:ERR", status=400)

class UserLoginView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, format=None):
        username = request.data['username']
        password = request.data['password']
        user_obj = CustomUser.objects.filter(email=username).first() or CustomUser.objects.filter(username=username).first()
        user_driver = get_object_or_404(CustomUserDriver, user=user_obj)

        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': password
            }

            user = authenticate(**credentials)

            if user and user.is_active:
                user_serializar = UserSerializers(user)
                driver_serializers = CustomUserDriverSerializer(user_driver)

                # Combina los datos de CustomUser y CustomUserDriver en un solo diccionario
                combined_data = {
                    'user': user_serializar.data,
                    'vehicle': driver_serializers.data,
                    'image_url': user_driver.image.url if user_driver.image else None,
                    'license_url': user_driver.license.url if user_driver.license else None
                }

                return Response(combined_data, status=200)
            elif (user_obj.role != 'conductor'):
                return Response("ERR: Usuario Ingresado no es un conductor", status=403)
            elif (user_obj.status != 'active'):
                return Response("ERR: Cuenta no activa", status=403)
                
        return Response("ERR: Credenciales invalidas", status=403)
    
class TransferStopViewSet(viewsets.ModelViewSet):
    queryset = TransferStop.objects.all()
    serializer_class = TransferStopSerializer

    def perform_create(self, serializer):
        # Guarda la instancia TransferStop
        transfer_stop = serializer.save()

        # Busca el TransferRequest con el mismo ID
        transfer_request_id = self.request.data.get("id")
        transfer_request = TransferRequest.objects.filter(id=transfer_request_id).first()

        if transfer_request:
            # Asigna la instancia TransferStop al campo stop_time de TransferRequest
            transfer_request.stop_time.add(transfer_stop)
            transfer_request.save()

        return Response({"message": "Guardado exitoso"}, status=200)

class DesviationViewSet(viewsets.ModelViewSet):
    queryset = Desviation.objects.all()
    serializer_class = DesviationSerializer

    def perform_create(self, serializer):
        # Guarda la instancia Desviation
        desviation = serializer.save()

        # Busca el TransferRequest con el mismo ID
        transfer_request_id = self.request.data.get("id")
        transfer_request = TransferRequest.objects.filter(id=transfer_request_id).first()

        if transfer_request:
            # Asigna la instancia Desviation al campo deviation de TransferRequest
            transfer_request.deviation.add(desviation)
            transfer_request.save()

        return Response({"message": "Guardado exitoso"}, status=200)
    
class SendOTPView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            otp_code = get_random_string(length=6, allowed_chars='0123456789')
            OTPCode.objects.create(user=user, code=otp_code)
            
            send_mail(
                'Your OTP Code',
                f'Your OTP code is {otp_code}',
                'from@example.com',
                [email],
                fail_silently=False,
            )
            
            return Response({"message": "OTP code sent to your email."}, status=status.HTTP_200_OK)
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    
class ValidateOTPView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            otp_record = OTPCode.objects.filter(user=user, code=otp_code).first()
            if otp_record:
                return Response({"message": "OTP code is valid."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)

class ChangePasswordView(APIView):
    def post(self, request, format=None):
        email = request.data.get('email')
        otp_code = request.data.get('otp_code')
        new_password = request.data.get('new_password')
        user = CustomUser.objects.filter(email=email).first()
        
        if user:
            otp_record = OTPCode.objects.filter(user=user, code=otp_code).first()
            if otp_record:
                user.set_password(new_password)
                user.save()
                otp_record.delete()  # Elimina el código OTP después de usarlo
                return Response({"message": "Password changed successfully."}, status=status.HTTP_200_OK)
            return Response({"error": "Invalid OTP code."}, status=status.HTTP_400_BAD_REQUEST)
        return Response({"error": "User with this email does not exist."}, status=status.HTTP_400_BAD_REQUEST)
    
class CustomUserDriverImageUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        user_driver = get_object_or_404(CustomUserDriver, user__id=user_id)
        
        image = request.FILES.get('image')
        license = request.FILES.get('license')

        if image:
            user_driver.image = image
        if license:
            user_driver.license = license
        
        user_driver.save()

        return Response({"message": "Imágenes subidas exitosamente"}, status=status.HTTP_200_OK)
    
class UserTransferRequestsView(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the CustomUser object
        user = get_object_or_404(CustomUser, id=user_id)

        # Get the CustomUserDriver object associated with the CustomUser
        user_driver = get_object_or_404(CustomUserDriver, user=user)

        # Get all TransferRequest objects where the driver is the CustomUserDriver
        transfer_requests = TransferRequest.objects.filter(user_driver=user_driver)

        # Serialize the TransferRequest objects
        serializer = TransferRequestSerializer(transfer_requests, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
class UpdateTransferRequestStatusView(APIView):
    def post(self, request, format=None):
        serializer = TransferRequestStatusUpdateSerializer(data=request.data)
        if serializer.is_valid():
            transfer_request_id = serializer.validated_data['id']
            new_status = serializer.validated_data['status']

            transfer_request = get_object_or_404(TransferRequest, id=transfer_request_id)
            transfer_request.status = new_status
            transfer_request.save()

            return Response({"id": transfer_request.id, "status": transfer_request.status}, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UploadComprobanteView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, format=None):
        transfer_request_id = request.data.get('id')
        comprobante = request.FILES.get('comprobante')

        if not transfer_request_id or not comprobante:
            return Response({"error": "ID del TransferRequest y comprobante son requeridos"}, status=status.HTTP_400_BAD_REQUEST)

        transfer_request = get_object_or_404(TransferRequest, id=transfer_request_id)
        transfer_request.comprobante = comprobante
        transfer_request.status = 'finalizada'
        transfer_request.save()

        return Response({"message": "Comprobante subido y estado actualizado a finalizada"}, status=status.HTTP_200_OK)
    
class DriverEarningsView(APIView):
    def post(self, request, format=None):
        user_driver_id = request.data.get('user_id')
        if not user_driver_id:
            return Response({"error": "User Driver ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        # Obtener el CustomUserDriver
        user_driver = get_object_or_404(CustomUserDriver, user__id=user_driver_id)

        # Consultar todos los TransferRequest con el user_driver y estado 'finalizada'
        transfer_requests = TransferRequest.objects.filter(user_driver=user_driver, status='finalizada',paid_driver=False)

        total_earnings = 0
        for transfer_request in transfer_requests:
            if transfer_request.is_round_trip:
                total_earnings += transfer_request.rate.driver_price_round_trip
            else:
                total_earnings += transfer_request.rate.driver_price

        return Response({"total_earnings": total_earnings}, status=status.HTTP_200_OK)

class TransferRequestDetailView(APIView):
    def post(self, request, format=None):
        transfer_request_id = request.data.get('id')
        if not transfer_request_id:
            return Response({"error": "TransferRequest ID is required"}, status=status.HTTP_400_BAD_REQUEST)

        transfer_request = get_object_or_404(TransferRequest, id=transfer_request_id)
        
        serialized_transfer = serialize("json", [transfer_request], use_natural_foreign_keys=True)
        serialized_transfer_data = json.loads(serialized_transfer)[0]  # Convertir a dict

        # Obtener el nombre y apellido del usuario
        user = transfer_request.service_requested
        try:
            user_full_name = f"{user.first_name} {user.last_name}"
        except:
            user_full_name = "Usuario invitado"

        # Obtener la URL completa de la imagen de la empresa
        if user.company and user.company.image:
            company_image_url = user.company.image.url
        else:
            company_image_url = ""

        # Obtener la información completa de las personas a trasladar
        persons_to_transfer = list(transfer_request.person_to_transfer.values('name', 'phone', 'company'))

        # Añadir el nombre y apellido, la URL de la imagen de la empresa y la información de las personas a trasladar al diccionario de la transferencia
        serialized_transfer_data['fields']['service_requested'] = user_full_name
        serialized_transfer_data['fields']['company_image_url'] = company_image_url
        serialized_transfer_data['fields']['person_to_transfer'] = persons_to_transfer

        # Serializar los desvíos
        serialized_deviations = serialize("json", transfer_request.deviation.all(), use_natural_foreign_keys=True)
        serialized_deviations_data = json.loads(serialized_deviations)

        # Añadir los desvíos al diccionario de la transferencia
        serialized_transfer_data['fields']['deviations'] = serialized_deviations_data
        serialized_transfer_data['fields']['id'] = transfer_request.id

        if transfer_request.is_round_trip:
            rates = {
                "driver_gain": str(transfer_request.rate.driver_price_round_trip)
            }
        else:
            rates = {
                "driver_gain": str(transfer_request.rate.driver_price)
            }

        return Response({
            "transferencia_id": transfer_request.id,
            "transferencia_data": serialized_transfer_data,  # No convertir a JSON string
            "rates": rates
        }, status=status.HTTP_200_OK)
