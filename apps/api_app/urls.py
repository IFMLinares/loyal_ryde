
from django.contrib import admin
from django.urls import path, include
from .views import *
# from rest_framework.views 

urlpatterns = [
    path('test', TestView.as_view()),
    path('create-user', UserView.as_view()),
    path('get-user', UserLoginView.as_view()),
    path('login-user/', UserLoginView.as_view()),
]
