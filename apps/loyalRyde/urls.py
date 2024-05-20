from django.urls import path, include
from .views import *

app_name = 'loyalRyde'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('transfer-request/create/', TransferRequestCreateView.as_view(), name='transfer_request_create'),
    path('transfer-request/list/', TransferRequestListView.as_view(), name='transfer_request_list'),
    
    
    # AJAX VIEWS
    path('transfer-request/people/create', get_people_transfer, name='transfer_request_people_create'),
    path('transfer-request/approve', approve_request, name='transfer_request_approve'),
    
]