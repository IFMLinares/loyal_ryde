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
                    'vehicle': driver_serializers.data
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
        user_driver_id = request.data.get('user_driver_id')
        user_driver = get_object_or_404(CustomUserDriver, id=user_driver_id)
        
        serializer = CustomUserDriverSerializer(user_driver, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
class UserTransferRequestsView(APIView):
    def post(self, request, format=None):
        user_id = request.data.get('user_id')
        if not user_id:
            return Response({"error": "User ID is required"}, status=status.HTTP_400_BAD_REQUEST)
        
        # Get the CustomUser object
        user = get_object_or_404(CustomUser, id=user_id)
        # print(f"User found: {user}")

        # Get the CustomUserDriver object associated with the CustomUser
        user_driver = get_object_or_404(CustomUserDriver, user=user)
        # print(f"UserDriver found: {user_driver}")

        # Get all TransferRequest objects where the driver is the CustomUserDriver
        transfer_requests = TransferRequest.objects.filter(user_driver=user_driver)
        # print(f"TransferRequests found: {transfer_requests}")

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