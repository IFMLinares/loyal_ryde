from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.shortcuts import get_object_or_404
from django.views.decorators.csrf import csrf_exempt

from ..loyalRyde.models import CustomUser, CustomUserDriver
from .serializers import UserSerializers, CustomUserDriverSerializer

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

    def get(self, request, format=None):
        if request.user.is_authenticated == False or request.user.is_active == False:
            return Response("Credenciales Invalidas", status=403)
        
        user = UserSerializers(request.user)
        print(user)

        return Response("TESTING", status=200)
    
    
    @csrf_exempt
    def post(self, request, format=None):
        user_obj = CustomUser.objects.filter(email=request.data['username']).first() or CustomUser.objects.filter(username=request.data['username']).first()
        user_driver = get_object_or_404(CustomUserDriver, user=user_obj)
        # CustomUserDriver.objects.get(user=user_obj)


        if user_obj is not None:
            credentials = {
                'username': user_obj.username,
                'password': request.data['password']
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