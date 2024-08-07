
from django.contrib import admin
from rest_framework.routers import DefaultRouter
from django.urls import path, include
from .views import *
# from rest_framework.views 

router = DefaultRouter()
router.register(r'transfer-stops', TransferStopViewSet)
router.register(r'desviations', DesviationViewSet)

urlpatterns = [
    path('', include(router.urls)),
    path('create-user', UserView.as_view()),
    path('get-user', UserLoginView.as_view()),
    path('login-user/', UserLoginView.as_view()),
]
