# models.py
# models.py
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.db import models
from django.contrib.auth.models import User

class Business(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField()
    password = models.CharField(max_length=128)  # Remove this line

    def __str__(self):
        return self.name


class UserBusinessLink(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='business_link')
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='users')
    userType = models.CharField(max_length=50, default='staff')

    class Meta:
        unique_together = ('user', 'business')


class Facility(models.Model):
    business = models.ForeignKey(Business, on_delete=models.CASCADE, related_name='facilities')
    facilityType = models.CharField(max_length=255)
    facilityName = models.CharField(max_length=255)
    facilityDescription = models.TextField()

    def __str__(self):
        return self.facilityName
    

class NormalFacility(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    monday_open = models.TimeField()
    monday_close = models.TimeField()
    tuesday_open = models.TimeField()
    tuesday_close = models.TimeField()
    wednesday_open = models.TimeField()
    wednesday_close = models.TimeField()
    thursday_open = models.TimeField()
    thursday_close = models.TimeField()
    friday_open = models.TimeField()
    friday_close = models.TimeField()
    saturday_open = models.TimeField()
    saturday_close = models.TimeField()
    sunday_open = models.TimeField()
    sunday_close = models.TimeField()
    slot_frequency = models.IntegerField()  # e.g., every 15 minutes
    slot_length = models.IntegerField()  # in minutes
    slot_price = models.DecimalField(max_digits=10, decimal_places=2)
    additional_minutes = models.IntegerField()
    additional_price = models.DecimalField(max_digits=10, decimal_places=2)
    slot_quantity = models.IntegerField()


class RestaurantFacility(models.Model):
    facility = models.ForeignKey(Facility, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    opening_time = models.TimeField()
    closing_time = models.TimeField()
    slot_frequency = models.IntegerField()  # e.g., every 15 minutes
    slot_length = models.IntegerField()  # in minutes
    slot_price = models.DecimalField(max_digits=10, decimal_places=2)
    tables_of_1 = models.PositiveIntegerField(default=0)
    tables_of_2 = models.PositiveIntegerField(default=0)
    tables_of_3 = models.PositiveIntegerField(default=0)
    tables_of_4 = models.PositiveIntegerField(default=0)
    tables_of_5 = models.PositiveIntegerField(default=0)
    tables_of_6 = models.PositiveIntegerField(default=0)
    tables_of_7 = models.PositiveIntegerField(default=0)
    tables_of_8 = models.PositiveIntegerField(default=0)
    tables_of_9 = models.PositiveIntegerField(default=0)
    tables_of_10 = models.PositiveIntegerField(default=0)
    tables_of_11 = models.PositiveIntegerField(default=0)
    tables_of_12 = models.PositiveIntegerField(default=0)
    monday_open = models.TimeField(default="09:00:00")
    monday_close = models.TimeField(default="18:00:00")
    tuesday_open = models.TimeField(default="09:00:00")
    tuesday_close = models.TimeField(default="18:00:00")
    wednesday_open = models.TimeField(default="09:00:00")
    wednesday_close = models.TimeField(default="18:00:00")
    thursday_open = models.TimeField(default="09:00:00")
    thursday_close = models.TimeField(default="18:00:00")
    friday_open = models.TimeField(default="09:00:00")
    friday_close = models.TimeField(default="18:00:00")
    saturday_open = models.TimeField(default="09:00:00")
    saturday_close = models.TimeField(default="18:00:00")
    sunday_open = models.TimeField(default="09:00:00")
    sunday_close = models.TimeField(default="18:00:00")

    def __str__(self):
        return self.name
    


class ClosedDate(models.Model):
    date = models.DateField()
    normal_facility = models.ForeignKey(NormalFacility, on_delete=models.CASCADE, null=True, blank=True)
    restaurant_facility = models.ForeignKey(RestaurantFacility, on_delete=models.CASCADE, null=True, blank=True)

    def __str__(self):
        return f"{self.date} - {self.normal_facility or self.restaurant_facility}"
    

class CloseNormalFacility(models.Model):
    normal_facility = models.ForeignKey(NormalFacility, on_delete=models.CASCADE)
    date = models.DateField()

    def __str__(self):
        return f"{self.date} - {self.normal_facility}"