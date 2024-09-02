
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
    path('send-otp/', SendOTPView.as_view(), name='send_otp'),
    path('validate-otp/', ValidateOTPView.as_view(), name='validate_otp'),
    path('change-password/', ChangePasswordView.as_view(), name='change_password'),
    path('upload-driver-image/', CustomUserDriverImageUploadView.as_view(), name='upload-driver-image'),
    path('user-transfer-requests/', UserTransferRequestsView.as_view(), name='user-transfer-requests'),
    path('update-transfer-request-status/', UpdateTransferRequestStatusView.as_view(), name='update_transfer_request_status'),
]