from django.urls import path, include
from .views_initial import *

# Importar vistas desde las diferentes carpetas
from apps.loyalRyde.views.arrival_views.views import *
from apps.loyalRyde.views.componaie_views.views import *
from apps.loyalRyde.views.departure_views.views import *
from apps.loyalRyde.views.discount_views.views import *
from apps.loyalRyde.views.driver_views.views import *
from apps.loyalRyde.views.fleet_views.views import *
from apps.loyalRyde.views.rates_views.views import *
from apps.loyalRyde.views.route_views.views import *
from apps.loyalRyde.views.transfers_request_views.views import *
from apps.loyalRyde.views.trips_views.views import *
from apps.loyalRyde.views.user_views.views import *

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
    path('update/operator/<int:pk>/', UserOperatorUpdateView.as_view(), name='update_user_operator'),
    path('update/supervisor/<int:pk>/', UserSupervisorUpdateView.as_view(), name='update_user_supervisor'),
    # delete user
    path('delete/user/<int:pk>/', DeleteUser.as_view(), name='delete_user'),
    path('company/list/', CompaniesListView.as_view(), name='companies_list'),
    path('company/create/', CompnayAdd.as_view(), name='companies_create'),
    path('drivers/create/', DriverAdd.as_view(), name='driver_add'),
    path('drivers/delete/<int:pk>/', DriverDeleteView.as_view(), name='driver_delete'),
    path('driver/update/<int:pk>/', DriverUpdateView.as_view(), name='driver_update'),
    path('drivers/list/', DriverListView.as_view(), name='driver_list'),
    path('drivers/list/active', DriverActiveListView.as_view(), name='driver_list_active'),
    path('drivers/list/inactive', DriverPendingListView.as_view(), name='driver_list_pending'),
    path('fleet/create/', FleetAdd.as_view(), name='fleet_add'),
    path('fleet/type/create', FleetTypeAdd.as_view(), name='fleet_add_type'),
    path('fleet/type/update/<int:pk>/', FleetTypeUpdateView.as_view(), name='fleet_type_update'),
    path('fleet/list/', FleetListView.as_view(), name='fleet_list'),
    path('fleet/type/list', FleeTypetListView.as_view(), name='fleet_list_type'),
    path('route/create/', RouteCreateView.as_view(), name='route_add'),
    path('route/departure/create', DeparturePointCreateView.as_view(), name='rates_departure_create'),
    path('route/departure/list', DepartureListView.as_view(), name='rates_departure_list'),
    path('route/departure/update/<int:pk>/', DepartureUpdateView.as_view(), name='departure_update'),
    path('route/arrival/create', ArrivalPointCreateView.as_view(), name='rates_arrival_create'),
    path('route/arrival/list', ArrivalListView.as_view(), name='rates_arrival_list'),
    path('route/arrival/update/<int:pk>/', ArrivalPointUpdateView.as_view(), name='arrival_update'),
    path('route/arrival/delete/<int:pk>/', ArrivalPointDeleteView.as_view(), name='arrival_delete'),
    path('route/departure/delete/<int:pk>/', DepartureDeleteView.as_view(), name='departure_delete'),
    path('route/list/', RouteListView.as_view(), name='route_list'),
    path('route/update/<int:pk>/', RouteUpdate.as_view(), name='route_update'),
    path('route/delete/<int:pk>/', RouteDeleteView.as_view(), name='route_delete'),
    path('trips/progress/', TripsProgressListView.as_view(), name='trips_progress'),
    path('trips/completed/', TripsCompletedListView.as_view(), name='trips_completed'),
    path('trips/hold/', TripsHoldListView.as_view(), name='trips_hold'),
    path('trips/approve/', TripsAroveListView.as_view(), name='trips_approve'),
    path('trips/programed/', TripsProgramedListView.as_view(), name='trips_programed'),
    path('trips/cancelled/', TripsCancelledListView.as_view(), name='trips_cancelled'),
    path('rates/list/', RatesListView.as_view(), name='rates_list'),
    path('rates/update/<int:pk>/', RatesUpdateView.as_view(), name='rates_update'),
    path('rates/delete/<int:pk>/', RatesDeleteView.as_view(), name='rates_delete'),
    path('rates/create/', RatesCreateView.as_view(), name='rates_create'),
    path('discount-coupon/create/', DiscountCouponCreateView.as_view(), name='discount_coupon_create'),
    path('discount-coupons/', DiscountCouponListView.as_view(), name='discount_coupon_list'),
    path('discount-coupon/update/<int:pk>/', DiscountCouponUpdateView.as_view(), name='discount_coupon_update'),
    path('discount-coupon/detail/<int:pk>/', DiscountCouponDetailView.as_view(), name='discount_coupon_detail'),
    path('discount-coupon/delete/', delete_coupon, name='discount_coupon_delete'),
    path('reports/excel/', TransferRequestExcelView.as_view(), name='transfer_request_excel'),
    path('reports/generales/', GeneralReportsView.as_view(), name='reportes_generales'),
    path('reports/company/', FilteredTransferRequestsView.as_view(), name='reports_company'),
    path('company/update/<int:pk>/', CompanyUpdateView.as_view(), name='company_update'),
    # perfil
    path('profile/', ProfileView.as_view(), name='profile'),
    # perfil
    
    
    # AJAX VIEWS
    path('transfer-request/people/create', get_people_transfer, name='transfer_request_people_create'),
    path('transfer-request/approve', approve_request, name='transfer_request_approve'),
    path('transfer-request/cancel/', cancel_request, name='transfer_request_cancel'),
    path('transfer-request/admin/approve/', approve_request_admin, name='transfer_request_approve_admin'),
    path('company/image', get_company_image, name='company_image'),
    path("transfer-request/routes", get_routes_by_departure, name="routes_ajax"),
    path("transfer-request/rates", get_rates, name="rates_ajax"),
    path('verify-discount-code/', verify_discount_code, name='verify_discount_code'),
    path('ajax/transfer-month/', transfer_requests_per_month, name='transfer_month'),
    path('drivers/payroll/', DriverPayrollView.as_view(), name='driver_payroll'),
    path('drivers/payroll/excel/<int:pk>/', DriverPayrollExcelView.as_view(), name='driver_payroll_excel'),
    path('transfer_request/<int:pk>/pdf/', TransferRequestPDFView.as_view(), name='transfer_request_pdf'),
    path('guest-transfer/success/<int:pk>/', GuestTransferSuccessView.as_view(), name='guest_transfer_success'),
    path('reports/company_filtered/', CompanyFilteredTransferRequestsView.as_view(), name='reports_company_filtered'),
]