from django.shortcuts import render
from rest_framework.views import APIView
from rest_framework.response import Response
from django.contrib.auth import authenticate
from django.contrib.auth.models import User

from ..loyalRyde.models import CustomUser
from .serializers import UserSerializers

# Create your views here.
class TestView(APIView):
    def get(self, request, fornmat=None):
        print("Funcionado")
        return Response("You made it", status=200)
    
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
    
    def post(self, request, format=None):
        print("Login class")
        user_obj = CustomUser.objects.filter(email=request.data['username']).first() or CustomUser.objects.filter(username=request.data['username']).first()

        if user_obj is not None:
            print(user_obj)
            credentials = {
                'username': user_obj.username,
                'password': request.data['password']
            }

            user = authenticate(**credentials)

            if user and user.is_active:
                user_serializar = UserSerializers(user)
                return Response(user_serializar.data, status=200)
        return Response("Credenciales invalidas", status=403)