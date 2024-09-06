# myapp/urls.py
from django.urls import path
from .views import *

urlpatterns = [
    path('signup/customer', customer_signup, name='customer_signup'),
    path('login/customer', customer_login, name='customer_login'),
    path('customer/home', customer_home, name='customer_home'),
    path('business/<int:business_id>/facilities', business_facilities, name='business_facilities'),
    path('facilities/cust/<int:facility_id>', facility_detail_cust, name='facility_detail_cust'),
    path('facilities/<int:facility_id>/book', book_facility, name='book_facility'),
    path('restaurant/book/<int:facility_id>', book_restaurant, name='book_restaurant'),
    path('book/<int:subfacility_id>/<str:selected_date>/<str:selected_time>', booking_confirmation, name='booking_confirmation'),
    path('book/extra/<int:subfacility_id>/<str:selected_date>/<str:selected_time>', booking_confirmation_extra, name='booking_confirmation_extra'),
    path('book/restaurant/<int:restaurant_facility_id>/<str:selected_date>/<str:selected_time>', restaurant_booking_confirmation, name='restaurant_booking_confirmation'),
    path('booking/success/', booking_success, name='booking_success'),
    path('delete/booking/<int:booking_id>', delete_booking, name='delete_booking'),
    path('bookings/<int:booking_id>/edit', edit_booking, name='edit_booking'),
    path('test-email/', test_email, name='test-email'),
    path('activate-account', activate_account, name='activate_account'),
    path("customer/profile", customerProfile, name="customerProfile"),
    path('payment/<int:booking_id>/', payment, name='payment'),
    path('create-payment-intent/<int:booking_id>/', create_payment_intent, name='create_payment_intent'),
    path("payment/success/<int:booking_id>/", payment_success, name="payment_success"),
    path('confirm-payment/<int:booking_id>/', confirm_payment, name='confirm_payment'),
    path('cancel-booking/<int:booking_id>/', cancel_booking, name='cancel_booking'),
    path('booking/cancelled/', booking_cancelled, name='booking_cancelled'),
    path('view/businesses', view_businesses, name='view_businesses'),
]

