from django.urls import path, include
from .views import *

app_name = 'loyalRyde'

urlpatterns = [
    path('', Index.as_view(), name='index'),
    path('transfer-request/create/', TransferRequestCreateView.as_view(), name='transfer_request_create'),
    path('transfer-request/guest/', GuestTransferCreateView.as_view(), name='transfer_request_create_guest'),
    path('transfer-request/list/', TransferRequestListView.as_view(), name='transfer_request_list'),
    path('transfer-request/detail/<int:pk>', TransferRequestDetailview.as_view(), name='transfer_request_detail'),
    path('transfer-request/update/<int:pk>', TransferRequestUpdateView.as_view(), name='transfer_request_update'),
    path('users/add/', UserAdd.as_view(), name='user_add'),
    path('users/add_company_user/', UserCompanyAdd.as_view(), name='user_add_company'),
    path('users/list-admin/', UserAdminListView.as_view(), name='user_list_admin'),
    path('users/list-dispatchers/', UserDispatchListView.as_view(), name='user_list_dispatcher'),
    path('users/list-operator/', UserOperatorListView.as_view(), name='user_list_operator'),
    path('users/list-supervisor/', UserSupervisorListView.as_view(), name='user_list_supervisor'),
    path('company/list/', CompaniesListView.as_view(), name='companies_list'),
    path('company/create/', CompnayAdd.as_view(), name='companies_create'),
    path('drivers/create/', DriverAdd.as_view(), name='driver_add'),
    path('drivers/list/', DriverListView.as_view(), name='driver_list'),
    path('drivers/list/active', DriverActiveListView.as_view(), name='driver_list_active'),
    path('drivers/list/inactive', DriverPendingListView.as_view(), name='driver_list_pending'),
    path('fleet/create/', FleetAdd.as_view(), name='fleet_add'),
    path('fleet/type/create', FleetTypeAdd.as_view(), name='fleet_add_type'),
    path('fleet/list/', FleetListView.as_view(), name='fleet_list'),
    path('fleet/type/list', FleeTypetListView.as_view(), name='fleet_list_type'),
    path('route/create/', RouteCreateView.as_view(), name='route_add'),
    path('route/departure/create', DeparturePointCreateView.as_view(), name='rates_departure_create'),
    path('route/departure/list', DepartureListView.as_view(), name='rates_departure_list'),
    path('route/arrival/create', ArrivalPointCreateView.as_view(), name='rates_arrival_create'),
    path('route/arrival/list', ArrivalListView.as_view(), name='rates_arrival_list'),
    path('route/list/', RouteListView.as_view(), name='route_list'),
    path('trips/progress/', TripsProgressListView.as_view(), name='trips_progress'),
    path('trips/completed/', TripsCompletedListView.as_view(), name='trips_completed'),
    path('trips/hold/', TripsHoldListView.as_view(), name='trips_hold'),
    path('trips/approve/', TripsAroveListView.as_view(), name='trips_approve'),
    path('trips/programed/', TripsProgramedListView.as_view(), name='trips_programed'),
    path('trips/cancelled/', TripsCancelledListView.as_view(), name='trips_cancelled'),
    path('rates/list/', RatesListView.as_view(), name='rates_list'),
    path('rates/create/', RatesCreateView.as_view(), name='rates_create'),
    
    
    
    # AJAX VIEWS
    path('transfer-request/people/create', get_people_transfer, name='transfer_request_people_create'),
    path('transfer-request/approve', approve_request, name='transfer_request_approve'),
    path('transfer-request/admin/approve/', approve_request_admin, name='transfer_request_approve_admin'),
    path('company/image', get_company_image, name='company_image'),
    path("transfer-request/routes", get_routes_by_departure, name="routes_ajax"),
    path("transfer-request/rates", get_rates, name="rates_ajax"),
    path('ajax/transfer-month/', transfer_requests_per_month, name='transfer_month'),
    
    
]