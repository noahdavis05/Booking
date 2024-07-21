from django import forms
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from .models import Customer, Booking

class CustomerSignupForm(UserCreationForm):
    email = forms.EmailField(required=True)
    first_name = forms.CharField(max_length=150, required=True)
    last_name = forms.CharField(max_length=150, required=True)
    phone_number = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)

    class Meta:
        model = User
        fields = ['email', 'password1', 'password2', 'first_name', 'last_name', 'phone_number', 'address']

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("A user with that email already exists.")
        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.username = self.cleaned_data['email']  # Set username to email
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']
        if commit:
            user.save()
            customer = Customer.objects.create(
                user=user, 
                phone_number=self.cleaned_data['phone_number'], 
                address=self.cleaned_data['address']
            )
        return user

class CustomerLoginForm(AuthenticationForm):
    username = forms.CharField(label="Username", max_length=254)
    password = forms.CharField(label="Password", widget=forms.PasswordInput)




class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['sub_facility', 'date', 'time','booking_notes']  
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'readonly': 'readonly'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'readonly': 'readonly'}),
        }

class BookingFormBusiness(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['date', 'time', 'paid', 'booking_notes']  
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'paid': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }

class BookingExtraForm(forms.Form):
    additional_slots = forms.MultipleChoiceField(
        widget=forms.CheckboxSelectMultiple,
        required=False
    )

    def __init__(self, *args, **kwargs):
        slot_choices = kwargs.pop('slot_choices', [])
        super().__init__(*args, **kwargs)
        self.fields['additional_slots'].choices = slot_choices


class ActivationForm(forms.Form):
    activation_code = forms.CharField(max_length=6, label="Activation Code")