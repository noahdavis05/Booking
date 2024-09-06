from django.contrib.auth.models import User
from django.db import models
from business.models import NormalFacility, RestaurantFacility, Business
from django.utils import timezone

class Customer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    # Add any additional customer-specific fields here
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    activation_code = models.CharField(max_length=6, blank=True)
    is_active = models.BooleanField(default=False)

    def __str__(self):
        return self.user.username


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)  # Allow null for guest bookings
    sub_facility = models.ForeignKey(NormalFacility, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    paid = models.BooleanField(default=False)  # Indicates if the booking is paid
    booking_notes = models.TextField(blank=True, null=True)  # Additional notes for the booking
    booking_timestamp = models.DateTimeField(default=timezone.now)  # Timestamp when the booking was created
    next_booking = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='previous_booking')
    payment = models.ForeignKey('Payment', on_delete=models.SET_NULL, null=True, blank=True)
    stripe_payment_id = models.CharField(max_length=255, blank=True, null=True)
    name = models.CharField(max_length=255, blank=True, null=True)  # Guest's name
    email = models.EmailField(blank=True, null=True)  # Guest's email

    def __str__(self):
        if self.user:
            return f"Booking by {self.user.username} for {self.sub_facility.name} on {self.date} at {self.time}"
        else:
            return f"Guest booking for {self.sub_facility.name} on {self.date} at {self.time}"
    
class RestaurantBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant_facility = models.ForeignKey(RestaurantFacility, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    table_size = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.restaurant_facility.name} on {self.date} at {self.time}, Table for {self.table_size}"
    
class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    stripe_payment_id = models.CharField(max_length=255, unique=True)
    company = models.ForeignKey(Business, on_delete=models.CASCADE)
    status = models.CharField(max_length=50, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        user_display = self.user.username if self.user else "Guest"
        return f"Payment {self.id} by {user_display} for {self.amount} to {self.company.name}"
