from django.shortcuts import render
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
from .serializers import UserSerializers, CustomUserDriverSerializer,TransferStopSerializer, DesviationSerializer

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