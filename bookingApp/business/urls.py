from django.urls import path, include
from .views import *

urlpatterns = [
    path("", landing, name="landing"),
    path("signup/business/", authViewBusiness, name="authViewBusiness"),
    path("signup/business/login", loginViewBusiness, name="loginViewBusiness"),
    path("signup/business/create", createNewBusiness, name="CreateNewBusiness"),
    path("business/dashboard", businessDashboard, name="businessDashboard"),
    path("logout", myLogout, name="myLogout"),
    path("business/login", loginBusiness, name="loginBusiness"),
    path("access_denied", accessDenied, name="accessDenied"),
    path("facilities/new", newFacility, name="newFacility"),
    path("facilities/<int:facility_id>", facility_detail, name="facility_detail"),
    path("sub-facilities/new/<int:facility_id>", newSubFacility, name="newSubFacility"),
    path("facility/group/delete/<int:facility_id>", deleteFacilityGroup, name="deleteFacilityGroup"),
    path("facility/delete/<int:facility_id>", deleteNormalFacility, name="deleteNormalFacility"),
    path("facility/edit/<int:facility_id>", editFacility, name="editFacility"),
    path("facility/rest/delete/<int:facility_id>", deleteRestFacility, name="deleteNormalFacility"),
    path("facility/rest/edit/<int:facility_id>", editRestFacility, name="editFacility"),
    path("facility/normal/close/<int:facility_id>", closeFacility, name="closeFacility"),
    path("facility/normal/re-open/<int:facility_id>/<str:selected_date>", openFacility, name="openFacility"),
    path("facility/normal/bookings/<int:facility_id>", facilityBookings, name="facilityBookings"),
    path("facility/normal/booking/view/<int:booking_id>", viewBooking, name="viewBooking"),
    path("facility/normal/booking/delete/<int:booking_id>", deleteBooking, name="deleteBooking"),
    path("facility/normal/booking/edit/<int:booking_id>", editBooking, name="editBooking"),
    path("activate-account-business", activate_account, name="activate_account_business"),
    path("stripe-key", manage_stripe_keys, name="manage_stripe_keys"),
    path("update/business", choose_change, name="account_settings"),
    path('update/business/change-password/', change_account_password, name='change_account_password'),
    path('update/business/details', update_business_details, name='change_account_email'),
    path('update/business/change-master-password', change_master_password, name='change_master_password'),
    path('update/business/change-email', change_email, name='change_email'),
    
]

