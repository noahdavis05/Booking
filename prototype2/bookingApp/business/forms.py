# forms.py
from django import forms
from .models import Business, Facility, NormalFacility, RestaurantFacility, ClosedDate, CloseNormalFacility
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from datetime import time
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

class BusinessSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set username to email
        if commit:
            user.save()
            # Create a Business profile here if necessary
        return user

class LoginForm(forms.Form):
    username = forms.CharField(max_length=150)
    password = forms.CharField(widget=forms.PasswordInput)


class BusinessForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), label="Master Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm Master Password")

    class Meta:
        model = Business
        fields = ['name', 'description', 'password']
        widgets = {
            'password': forms.PasswordInput(),  # Render password field as a password input
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password and confirm_password and password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        business = super().save(commit=False)
        business.password = make_password(self.cleaned_data["password"])
        if commit:
            business.save()
        return business


class FacilityForm(forms.ModelForm):
    business_password = forms.CharField(widget=forms.PasswordInput, required=True)
    facilityType = forms.ChoiceField(choices=[('Sports', 'Sports'), ('Restaurant', 'Restaurant'), ('Generic', 'Generic')])

    class Meta:
        model = Facility
        fields = ['facilityType', 'facilityName', 'facilityDescription']

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super(FacilityForm, self).__init__(*args, **kwargs)
        if not self.business:
            raise ValueError("Business object is required")

    def clean_business_password(self):
        business_password = self.cleaned_data.get('business_password')
        if self.business and not check_password(business_password, self.business.password):
            raise forms.ValidationError("Invalid business password.")
        return business_password
    

class NormalFacilityForm(forms.ModelForm):
    business_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = NormalFacility
        fields = ['name', 'description', 'opening_time', 'closing_time', 'slot_frequency', 'slot_length', 'slot_quantity', 'slot_price','additional_minutes', 'additional_price',
              'monday_open', 'monday_close', 'tuesday_open', 'tuesday_close', 'wednesday_open', 'wednesday_close',
              'thursday_open', 'thursday_close', 'friday_open', 'friday_close', 'saturday_open', 'saturday_close',
              'sunday_open', 'sunday_close']

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super(NormalFacilityForm, self).__init__(*args, **kwargs)
        if not self.business:
            raise ValueError("Business object is required")
        
         # Set default values for opening_time and closing_time
        self.fields['opening_time'].initial = time(9, 0)
        self.fields['closing_time'].initial = time(18, 0)

        # Set these fields as hidden
        self.fields['opening_time'].widget = forms.HiddenInput()
        self.fields['closing_time'].widget = forms.HiddenInput()

    def clean_business_password(self):
        business_password = self.cleaned_data.get('business_password')
        if self.business and not check_password(business_password, self.business.password):
            raise forms.ValidationError("Invalid business password.")
        return business_password
    


class RestaurantFacilityForm(forms.ModelForm):
    business_password = forms.CharField(widget=forms.PasswordInput, required=True)

    class Meta:
        model = RestaurantFacility
        fields = [
            'name', 'description', 'opening_time', 'closing_time', 'slot_frequency',
            'slot_length', 'slot_price', 'tables_of_1', 'tables_of_2', 'tables_of_3',
            'tables_of_4', 'tables_of_5', 'tables_of_6', 'tables_of_7', 'tables_of_8',
            'tables_of_9', 'tables_of_10', 'tables_of_11', 'tables_of_12','monday_open', 'monday_close', 'tuesday_open', 'tuesday_close', 
            'wednesday_open', 'wednesday_close', 'thursday_open', 'thursday_close', 
            'friday_open', 'friday_close', 'saturday_open', 'saturday_close', 
            'sunday_open', 'sunday_close',
        ]

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super(RestaurantFacilityForm, self).__init__(*args, **kwargs)
        if not self.business:
            raise ValueError("Business object is required")
        
        self.fields['opening_time'].initial = time(9, 0)
        self.fields['closing_time'].initial = time(18, 0)

        # Set these fields as hidden
        self.fields['opening_time'].widget = forms.HiddenInput()
        self.fields['closing_time'].widget = forms.HiddenInput()

    def clean_business_password(self):
        business_password = self.cleaned_data.get('business_password')
        if self.business and not check_password(business_password, self.business.password):
            raise forms.ValidationError("Invalid business password.")
        return business_password
    
    
class ConfirmDeleteForm(forms.Form):
    password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")





    
class CloseNormalFacilityForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    class Meta:
        model = CloseNormalFacility
        fields = ['date', 'password']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['date'].widget = forms.DateInput(attrs={
            'type': 'date',
            'class': 'form-control',
        })

