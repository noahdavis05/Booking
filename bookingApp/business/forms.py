# forms.py
from django import forms
from .models import Business, Facility, NormalFacility, RestaurantFacility, ClosedDate, CloseNormalFacility, StripeKey
from django.contrib.auth.hashers import make_password
from django.contrib.auth.hashers import check_password
from datetime import time
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.contrib.auth.forms import PasswordChangeForm
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit
from crispy_forms.layout import Layout, Field, ButtonHolder, Submit
from django.core.exceptions import ValidationError


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
    facilityType = forms.ChoiceField(choices=[('Sports', 'Sports'),  ('Generic', 'Generic')])

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
        fields = [
            'name', 'description', 'opening_time', 'closing_time', 'slot_frequency',
            'slot_length', 'slot_quantity', 'slot_price',
            'monday_open', 'monday_close', 'tuesday_open', 'tuesday_close',
            'wednesday_open', 'wednesday_close', 'thursday_open', 'thursday_close',
            'friday_open', 'friday_close', 'saturday_open', 'saturday_close', 'sunday_open', 'sunday_close'
        ]
        widgets = {
            'opening_time': forms.HiddenInput(attrs={'id': 'id_opening_time'}),
            'closing_time': forms.HiddenInput(attrs={'id': 'id_closing_time'}),
            'monday_open': forms.TimeInput(attrs={'id': 'id_monday_open', 'type': 'time'}),
            'monday_close': forms.TimeInput(attrs={'id': 'id_monday_close', 'type': 'time'}),
            'tuesday_open': forms.TimeInput(attrs={'id': 'id_tuesday_open', 'type': 'time'}),
            'tuesday_close': forms.TimeInput(attrs={'id': 'id_tuesday_close', 'type': 'time'}),
            'wednesday_open': forms.TimeInput(attrs={'id': 'id_wednesday_open', 'type': 'time'}),
            'wednesday_close': forms.TimeInput(attrs={'id': 'id_wednesday_close', 'type': 'time'}),
            'thursday_open': forms.TimeInput(attrs={'id': 'id_thursday_open', 'type': 'time'}),
            'thursday_close': forms.TimeInput(attrs={'id': 'id_thursday_close', 'type': 'time'}),
            'friday_open': forms.TimeInput(attrs={'id': 'id_friday_open', 'type': 'time'}),
            'friday_close': forms.TimeInput(attrs={'id': 'id_friday_close', 'type': 'time'}),
            'saturday_open': forms.TimeInput(attrs={'id': 'id_saturday_open', 'type': 'time'}),
            'saturday_close': forms.TimeInput(attrs={'id': 'id_saturday_close', 'type': 'time'}),
            'sunday_open': forms.TimeInput(attrs={'id': 'id_sunday_open', 'type': 'time'}),
            'sunday_close': forms.TimeInput(attrs={'id': 'id_sunday_close', 'type': 'time'}),
        }

        help_texts = {
            'slot_frequency': 'The interval at which booking slots are available (e.g., every 30 minutes). Note this doesn\'t have to be the length as the slot but the slot length must be divisible by this number.',
            'slot_length': 'The duration of each booking slot (e.g., 1 hour).',
            'slot_quantity': 'The number of bookings which are allowed at any given time. For example, 4 different people could use a huge field at the same time, so slot quantity would be 4. Note, for most facilities this number will be 1.',
            'slot_price': 'The price for booking a single slot.',
        }

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

    def clean(self):
        cleaned_data = super().clean()
        slot_length = cleaned_data.get('slot_length')
        slot_frequency = cleaned_data.get('slot_frequency')

        if slot_length and slot_frequency:
            if slot_length % slot_frequency != 0:
                raise ValidationError("Slot length must be divisible by slot frequency.")
        
        return cleaned_data

    def save(self, commit=True):
        # Ensure additional_minutes and additional_price are set to 0 before saving
        self.instance.additional_minutes = 0
        self.instance.additional_price = 0
        return super().save(commit=commit)


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

class StripeKeyForm(forms.ModelForm):
    master_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Master Password",
        help_text="Enter your business account's master password to confirm changes.",
    )

    class Meta:
        model = StripeKey
        fields = ['public_key', 'secret_key', 'master_password']
        widgets = {
            'secret_key': forms.PasswordInput(),  # Hide the secret key field
            'webhook_secret': forms.HiddenInput(),  # Hide the webhook secret field
        }

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super(StripeKeyForm, self).__init__(*args, **kwargs)

    def clean_master_password(self):
        master_password = self.cleaned_data.get('master_password')
        if not check_password(master_password, self.business.password):
            raise forms.ValidationError("Incorrect master password.")
        return master_password
    

class MasterPasswordMixin(forms.Form):
    master_password = forms.CharField(widget=forms.PasswordInput(), label="Master Password")

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if not self.business:
            raise ValueError("Business object is required")
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Submit', css_class='btn btn-primary'))

    def clean_master_password(self):
        master_password = self.cleaned_data.get('master_password')
        if not self.business or not check_password(master_password, self.business.password):
            raise forms.ValidationError("Incorrect master password.")
        return master_password


class ChangeEmailForm(forms.ModelForm):
    confirm_email = forms.EmailField(required=True, label="Confirm New Email Address")
    master_password = forms.CharField(widget=forms.PasswordInput(), label="Master Password")

    class Meta:
        model = User
        fields = ['email']

    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        if not self.user:
            raise ValueError("User object is required")
        
        self.business = kwargs.pop('business', None)
        if not self.business:
            raise ValueError("Business object is required")
        
        super().__init__(*args, **kwargs)
        
        # Initialize Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('email', css_class='form-control'),
            Field('confirm_email', css_class='form-control'),
            Field('master_password', css_class='form-control'),
            ButtonHolder(
                Submit('submit', 'Change Email', css_class='btn btn-primary')
            )
        )

    def clean(self):
        cleaned_data = super().clean()
        self.email = cleaned_data.get('email')
        email = self.email
        confirm_email = cleaned_data.get('confirm_email')
        master_password = cleaned_data.get('master_password')

        # Check if emails match
        if email and confirm_email and email != confirm_email:
            self.add_error('confirm_email', 'Email addresses must match.')

        # Check if master password is correct
        if master_password and not check_password(master_password, self.business.password):
            self.add_error('master_password', 'Incorrect master password.')

        # Check for duplicate email
        if email and User.objects.filter(email=email).exclude(pk=self.user.pk).exists():
            self.add_error('email', 'This email address is already in use.')

        # Check for duplicate username
        if email and User.objects.filter(username=email).exclude(pk=self.user.pk).exists():
            self.add_error('email', 'This email address is already used as a username.')

        return cleaned_data

    def save(self, commit=True):
        self.user.email = self.email
        self.user.username = self.email
        self.user.save()

class ChangeMasterPasswordForm(forms.ModelForm):
    old_password = forms.CharField(widget=forms.PasswordInput(), label="Current Master Password")
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Master Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Master Password")

    class Meta:
        model = Business
        fields = []

    def __init__(self, *args, **kwargs):
        self.business = kwargs['instance']
        super().__init__(*args, **kwargs)

    def clean(self):
        cleaned_data = super().clean()
        old_password = cleaned_data.get("old_password")
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        # Validate old password
        if not check_password(old_password, self.business.password):
            self.add_error('old_password', "Current master password is incorrect.")

        # Validate new password and confirmation match
        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "New passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        business = self.instance
        business.password = make_password(self.cleaned_data["new_password"])
        if commit:
            business.save()
        return business

class ChangeAccountPasswordForm(forms.Form):
    master_password = forms.CharField(widget=forms.PasswordInput(), label="Master Password")
    new_password = forms.CharField(widget=forms.PasswordInput(), label="New Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput(), label="Confirm New Password")

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        self.user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if not self.business or not self.user:
            raise ValueError("Business and User objects are required")

        # Add Crispy Forms helper
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Change Password', css_class='btn btn-primary'))

    def clean_master_password(self):
        master_password = self.cleaned_data.get('master_password')
        if not check_password(master_password, self.business.password):
            raise forms.ValidationError("Incorrect master password.")
        return master_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get("new_password")
        confirm_password = cleaned_data.get("confirm_password")

        if new_password and confirm_password and new_password != confirm_password:
            self.add_error('confirm_password', "Passwords do not match")

        return cleaned_data

    def save(self, commit=True):
        self.user.set_password(self.cleaned_data['new_password'])
        if commit:
            self.user.save()
        return self.user


class UpdateBusinessDetailsForm(forms.ModelForm):
    master_password = forms.CharField(
        widget=forms.PasswordInput(),
        label="Master Password",
        required=True
    )

    class Meta:
        model = Business
        fields = ['name', 'description']

    def __init__(self, *args, **kwargs):
        self.business = kwargs.pop('business', None)
        super().__init__(*args, **kwargs)
        if not self.business:
            raise ValueError("Business object is required")
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.add_input(Submit('submit', 'Update Business Details', css_class='btn btn-primary'))

    def clean_master_password(self):
        master_password = self.cleaned_data.get('master_password')
        if not check_password(master_password, self.business.password):
            raise forms.ValidationError("Incorrect master password.")
        return master_password

    def save(self, commit=True):
        business = super().save(commit=False)
        if commit:
            business.save()
        return business