from django.contrib.auth.models import User
from django.db import models
from business.models import NormalFacility, RestaurantFacility

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
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    sub_facility = models.ForeignKey(NormalFacility, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    paid = models.BooleanField(default=False)
    booking_notes = models.TextField(blank=True, null=True)  # Add this line

    def __str__(self):
        return f"Booking by {self.user.username} for {self.sub_facility.name} on {self.date} at {self.time}"
    
class RestaurantBooking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant_facility = models.ForeignKey(RestaurantFacility, on_delete=models.CASCADE)
    date = models.DateField()
    time = models.TimeField()
    table_size = models.PositiveIntegerField()
    paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking by {self.user.username} for {self.restaurant_facility.name} on {self.date} at {self.time}, Table for {self.table_size}"