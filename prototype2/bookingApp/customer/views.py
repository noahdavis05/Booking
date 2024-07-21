from django.shortcuts import render, redirect,  get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.forms import AuthenticationForm
from .forms import CustomerSignupForm, CustomerLoginForm, BookingForm, BookingFormBusiness, ActivationForm
from django.contrib.auth.decorators import login_required
from .models import Customer, Booking, RestaurantBooking
from django.contrib import messages
from business.models import *
import datetime
from django.db.models import Q
from django.utils.dateparse import parse_date
from django.http import Http404
from .decorators import login_required_customer, login_required_business
from django.db import transaction, DatabaseError
from django import forms
import random
import string
from django.core.mail import send_mail
from django.http import HttpResponse

# for emails
def test_email(request):
    subject = 'Test Email from Django'
    message = 'This is a test email sent from Django using Brevo SMTP.'
    from_email = 'noah@thedavisfamily.org.uk'
    recipient_list = ['noah@thedavisfamily.org.uk']
    
    send_mail(subject, message, from_email, recipient_list)
    
    return HttpResponse("Email sent successfully!")

# sign up functions including emails
def generate_activation_code(length=6):
    return ''.join(random.choices(string.ascii_uppercase + string.digits, k=length))

# send the user the email to give them the activation code
def send_activation_email(user):
    subject = 'Your Activation Code'
    message = f'Your activation code is {user.customer.activation_code}.'
    from_email = 'noah@thedavisfamily.org.uk'
    recipient_list = [user.email]
    send_mail(subject, message, from_email, recipient_list)

# view to verify the user 
@login_required_customer
def activate_account(request):
    form = ActivationForm()
    if request.method == 'POST':
        if 'activate' in request.POST:
            form = ActivationForm(request.POST)
            if form.is_valid():
                activation_code = form.cleaned_data['activation_code']
                customer = request.user.customer
                if customer.activation_code == activation_code:
                    customer.is_active = True
                    customer.user.is_active = True
                    customer.user.save()
                    customer.save()
                    messages.success(request, 'Your account has been activated successfully.')
                    return redirect('/customer/home')
                else:
                    form.add_error('activation_code', 'Invalid activation code')
        elif 'resend_code' in request.POST:
            customer = request.user.customer
            customer.activation_code = generate_activation_code()
            customer.save()
            send_activation_email(request.user)
            messages.success(request, 'A new activation code has been sent to your email.')

    else:
        form = ActivationForm()
    
    return render(request, 'activate_account.html', {'form': form, 'email': request.user.email})

# sign up view
def customer_signup(request):
    if request.method == 'POST':
        form = CustomerSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_active = True  # Deactivate account till it is confirmed
            user.save()
            activation_code = generate_activation_code()
            # Create and save the Customer instance
            customer = Customer.objects.create(
                user=user,
                activation_code=activation_code,
                is_active=False  # Ensure the customer is inactive initially
            )
            send_activation_email(user)
            
            print("email snet")
            return redirect('/login/customer')  # Redirect to a page to enter the activation code
    else:
        form = CustomerSignupForm()
    return render(request, 'signup.html', {'form': form})

def customer_login(request):
    if request.method == 'POST':
        form = CustomerLoginForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect('/customer/home')  # Redirect to a customer-specific home page
    else:
        form = CustomerLoginForm()
    return render(request, 'myLogin.html', {'form': form})

@login_required_customer
def customer_home(request):
    try:
        
        if request.user.customer.is_active == False:
            return redirect('/activate-account')
    except:
        pass
    existing_bookings = Booking.objects.filter(user=request.user).order_by('date', 'time')
    restaurant_reservations = RestaurantBooking.objects.filter(user=request.user)
    return render(request, 'customerHome.html', {'bookings': existing_bookings, 'restaurant_reservations': restaurant_reservations})


def business_facilities(request, business_id):
    business = get_object_or_404(Business, id=business_id)
    facilities = Facility.objects.filter(business=business)
    return render(request, 'businessFacilities.html', {'business': business, 'facilities': facilities})

#not used
def facility_detail_cust(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)
    return render(request, 'facilityDetailCust.html', {'facility': facility})


# login not required, anyone should be able to browse but must be logged in to book.
"""
This is a view which gives the user's slots to book for a specific generic/sports facility.
If they are trying to book a restaurant facility, they will be redirected to the restaurant booking page.
"""
def book_facility(request, facility_id, selected_date=None):
    facility = get_object_or_404(Facility, id=facility_id)

    # Fetch the sub-facilities based on the facility type
    if facility.facilityType in ['Sports', 'Generic']:
        sub_facilities = NormalFacility.objects.filter(facility=facility)
    elif facility.facilityType == 'Restaurant':
        # redirect to restaurant booking page
        return redirect('/restaurant/book/' + str(facility_id))
    else:
        sub_facilities = []

    # Get the selected date from the GET parameters, default to today if not provided
    selected_date_str = request.GET.get('date', None)
    if selected_date_str:
        selected_date = parse_date(selected_date_str)
    else:
        selected_date = datetime.date.today()

   
    

    # Calculate available slots for each sub-facility
    slots = {}  # Dictionary to store available slots for each sub-facility
    for sub in sub_facilities:
        closed_dates = CloseNormalFacility.objects.filter(normal_facility=sub)
        if closed_dates.filter(date=selected_date).exists():
            slots[sub.id] = []
            continue
        # Get the day of the week for the selected date (0 = Monday, 6 = Sunday)
        day_of_week = selected_date.weekday()

        # Determine opening and closing times based on the day of the week
        if day_of_week == 0:  # Monday
            opening_time = sub.monday_open
            closing_time = sub.monday_close
        elif day_of_week == 1:  # Tuesday
            opening_time = sub.tuesday_open
            closing_time = sub.tuesday_close
        elif day_of_week == 2:  # Wednesday
            opening_time = sub.wednesday_open
            closing_time = sub.wednesday_close
        elif day_of_week == 3:  # Thursday
            opening_time = sub.thursday_open
            closing_time = sub.thursday_close
        elif day_of_week == 4:  # Friday
            opening_time = sub.friday_open
            closing_time = sub.friday_close
        elif day_of_week == 5:  # Saturday
            opening_time = sub.saturday_open
            closing_time = sub.saturday_close
        elif day_of_week == 6:  # Sunday
            opening_time = sub.sunday_open
            closing_time = sub.sunday_close

        # Calculate the available slots for the sub-facility on the given date
        existing_bookings = Booking.objects.filter(sub_facility=sub, date=selected_date)
        slot_times = []  # List to store available slots starting times
        current_time = datetime.datetime.combine(selected_date, opening_time)
        end_time = datetime.datetime.combine(selected_date, closing_time)
        slot_frequency = datetime.timedelta(minutes=sub.slot_frequency)

        while current_time < end_time:
            #iterate through bookings
            bookings_at_slot = 0
            for booking in existing_bookings:
                booking_start = datetime.datetime.combine(selected_date, booking.time)
                booking_end = booking_start + datetime.timedelta(minutes=sub.slot_length)
                if current_time < booking_end and (current_time + datetime.timedelta(minutes=sub.slot_length)) > booking_start:
                    bookings_at_slot += 1
            # Count the number of existing bookings for this time slot
            
            if bookings_at_slot < sub.slot_quantity:
                slot_times.append(str(current_time.time()))
            current_time += slot_frequency

        slots[sub.id] = slot_times

    return render(request, 'bookFacility.html', {
        'facility': facility,
        'sub_facilities': sub_facilities,
        'slots': slots,
        'selected_date': selected_date.strftime('%Y-%m-%d')
    })
"""
This view is for booking a restaurant facility. It will show the user the available slots for the restaurant facility.
"""
def book_restaurant(request, facility_id):
    facility = get_object_or_404(Facility, id=facility_id)

    if facility.facilityType not in ['Restaurant']:
        return redirect('/facilities/' + str(facility_id) + '/book')
    
    sub_facilities = RestaurantFacility.objects.filter(facility=facility)
    
    selected_date_str = request.GET.get('date', None)
    people = int(request.GET.get('people', 1))
    print(people, selected_date_str)

    if selected_date_str:
        selected_date = parse_date(selected_date_str)
    else:
        selected_date = datetime.date.today()

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = selected_date.weekday()

    slots = {}
    for sub in sub_facilities:
        existing_bookings = RestaurantBooking.objects.filter(restaurant_facility=sub, date=selected_date, table_size=people)
        slot_times = []
        
        if day_of_week == 0:
            opening_time = sub.monday_open
            closing_time = sub.monday_close
        elif day_of_week == 1:
            opening_time = sub.tuesday_open
            closing_time = sub.tuesday_close
        elif day_of_week == 2:
            opening_time = sub.wednesday_open
            closing_time = sub.wednesday_close
        elif day_of_week == 3:
            opening_time = sub.thursday_open
            closing_time = sub.thursday_close
        elif day_of_week == 4:
            opening_time = sub.friday_open
            closing_time = sub.friday_close
        elif day_of_week == 5:
            opening_time = sub.saturday_open
            closing_time = sub.saturday_close
        elif day_of_week == 6:
            opening_time = sub.sunday_open
            closing_time = sub.sunday_close

        current_time = datetime.datetime.combine(selected_date, opening_time)
        end_time = datetime.datetime.combine(selected_date, closing_time)
        slot_frequency = datetime.timedelta(minutes=sub.slot_frequency)
        slot_length = datetime.timedelta(minutes=sub.slot_length)
        tables = [sub.tables_of_1, sub.tables_of_2, sub.tables_of_3, sub.tables_of_4, sub.tables_of_5, sub.tables_of_6, sub.tables_of_7, sub.tables_of_8, sub.tables_of_9, sub.tables_of_10, sub.tables_of_11, sub.tables_of_12]
        selected_table_num = tables[people - 1]

        if tables[people - 1] == 0:
            slots[sub.id] = slot_times
        else:
            while current_time <= end_time - slot_length:
                tables_remaining = selected_table_num
                for booking in existing_bookings:
                    booking_start = datetime.datetime.combine(selected_date, booking.time)
                    booking_end = booking_start + slot_length
                    if current_time < booking_end and (current_time + slot_length) > booking_start:
                        tables_remaining -= 1
                        if tables_remaining == 0:
                            break
                    elif booking.time == current_time:
                        tables_remaining -= 1
                        if tables_remaining == 0:
                            break

                if tables_remaining > 0:
                    slot_times.append(str(current_time.time()))

                current_time += slot_frequency

        slots[sub.id] = slot_times

    return render(request, 'bookRestaurant.html', {
        'facility': facility,
        'sub_facilities': sub_facilities,
        'slots': slots,
        'selected_date': selected_date.strftime('%Y-%m-%d'),
        'people': people
    })



@login_required_customer
def booking_confirmation(request, subfacility_id, selected_date, selected_time):
    sub_facility = get_object_or_404(NormalFacility, id=subfacility_id)

    # Parse selected_date and selected_time
    try:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        selected_time = datetime.datetime.strptime(selected_time, '%H:%M:%S').time()
    except ValueError:
        raise Http404("Invalid date or time format")
    
    # Check if the sub-facility is closed on the selected date
    closed_dates = CloseNormalFacility.objects.filter(normal_facility=sub_facility)
    if closed_dates.filter(date=selected_date).exists():
        raise Http404("Sub-facility is closed on the selected date")

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = selected_date.weekday()

    # Map the day of the week to the corresponding opening and closing times
    opening_time = None
    closing_time = None
    if day_of_week == 0:
        opening_time = sub_facility.monday_open
        closing_time = sub_facility.monday_close
    elif day_of_week == 1:
        opening_time = sub_facility.tuesday_open
        closing_time = sub_facility.tuesday_close
    elif day_of_week == 2:
        opening_time = sub_facility.wednesday_open
        closing_time = sub_facility.wednesday_close
    elif day_of_week == 3:
        opening_time = sub_facility.thursday_open
        closing_time = sub_facility.thursday_close
    elif day_of_week == 4:
        opening_time = sub_facility.friday_open
        closing_time = sub_facility.friday_close
    elif day_of_week == 5:
        opening_time = sub_facility.saturday_open
        closing_time = sub_facility.saturday_close
    elif day_of_week == 6:
        opening_time = sub_facility.sunday_open
        closing_time = sub_facility.sunday_close

    # Validate that the selected time is within the opening hours
    if not (opening_time <= selected_time <= closing_time):
        raise Http404("Selected time is outside of the facility's opening hours")

    if request.method == 'POST':
        with transaction.atomic():
            existing_bookings = Booking.objects.select_for_update().filter(sub_facility=sub_facility, date=selected_date, time=selected_time)

            # Check if the number of existing bookings is less than the slot quantity
            if existing_bookings.count() >= sub_facility.slot_quantity:
                raise Http404("You were pipped to the post! Someone else has booked this slot")

            # Create the Booking instance with the sub_facility instance
            booking = Booking(
                user=request.user,
                sub_facility=sub_facility,
                date=selected_date,
                time=selected_time,
                paid=True
            )
            booking.save()
            return redirect('/booking/success')  # Redirect to a success page or another page

    return render(request, 'bookingConfirmation.html', {
        'subfacility_id': subfacility_id,
        'selected_date': selected_date,
        'selected_time': selected_time
    })

@login_required_customer
def booking_confirmation_extra(request, subfacility_id, selected_date, selected_time):
    sub_facility = get_object_or_404(NormalFacility, id=subfacility_id)

    # Parse selected_date and selected_time
    try:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        selected_time = datetime.datetime.strptime(selected_time, '%H:%M:%S').time()
    except ValueError:
        raise Http404("Invalid date or time format")

    # Check if the sub-facility is closed on the selected date
    closed_dates = CloseNormalFacility.objects.filter(normal_facility=sub_facility)
    if closed_dates.filter(date=selected_date).exists():
        raise Http404("Sub-facility is closed on the selected date")

    # Get the day of the week (0 = Monday, 6 = Sunday)
    day_of_week = selected_date.weekday()

    # Map the day of the week to the corresponding opening and closing times
    opening_time = None
    closing_time = None
    if day_of_week == 0:
        opening_time = sub_facility.monday_open
        closing_time = sub_facility.monday_close
    elif day_of_week == 1:
        opening_time = sub_facility.tuesday_open
        closing_time = sub_facility.tuesday_close
    elif day_of_week == 2:
        opening_time = sub_facility.wednesday_open
        closing_time = sub_facility.wednesday_close
    elif day_of_week == 3:
        opening_time = sub_facility.thursday_open
        closing_time = sub_facility.thursday_close
    elif day_of_week == 4:
        opening_time = sub_facility.friday_open
        closing_time = sub_facility.friday_close
    elif day_of_week == 5:
        opening_time = sub_facility.saturday_open
        closing_time = sub_facility.saturday_close
    elif day_of_week == 6:
        opening_time = sub_facility.sunday_open
        closing_time = sub_facility.sunday_close

    # Validate that the selected time is within the opening hours
    if not (opening_time <= selected_time <= closing_time):
        raise Http404("Selected time is outside of the facility's opening hours")

    if request.method == 'POST':
        additional_slots = request.POST.getlist('additional_slots')
        slots_to_book = [(selected_date, selected_time)] + [
            (selected_date, datetime.datetime.strptime(slot, '%H:%M').time()) for slot in additional_slots
        ]

        with transaction.atomic():
            for date, time in slots_to_book:
                existing_bookings = Booking.objects.select_for_update().filter(sub_facility=sub_facility, date=date, time=time)
                if existing_bookings.count() >= sub_facility.slot_quantity:
                    raise Http404("You were pipped to the post! Someone else has booked one of the selected slots")

            for date, time in slots_to_book:
                booking = Booking(
                    user=request.user,
                    sub_facility=sub_facility,
                    date=date,
                    time=time,
                    paid=True
                )
                booking.save()
            return redirect('/booking/success')  # Redirect to a success page or another page

    # Calculate available additional slots
    existing_bookings = Booking.objects.filter(sub_facility=sub_facility, date=selected_date)
    slot_times = []
    current_time = datetime.datetime.combine(selected_date, opening_time)
    end_time = datetime.datetime.combine(selected_date, closing_time)
    slot_frequency = datetime.timedelta(minutes=sub_facility.slot_frequency)
    slot_length = datetime.timedelta(minutes=sub_facility.slot_length)

    while current_time + slot_length <= end_time:
        if not existing_bookings.filter(time=current_time.time()).exists():
            slot_times.append(current_time.strftime('%H:%M'))
        current_time += slot_frequency

    return render(request, 'bookingConfirmationExtra.html', {
        'subfacility_id': subfacility_id,
        'selected_date': selected_date,
        'selected_time': selected_time.strftime('%H:%M'),
        'slot_times': slot_times
    })



@login_required_customer
def restaurant_booking_confirmation(request, restaurant_facility_id, selected_date, selected_time, people=1):
    sub_facility = get_object_or_404(RestaurantFacility, id=restaurant_facility_id)
    people = int(request.GET.get('people', people))

    # Parse selected_date and selected_time
    try:
        selected_date = datetime.datetime.strptime(selected_date, '%Y-%m-%d').date()
        selected_time = datetime.datetime.strptime(selected_time, '%H:%M:%S').time()
    except ValueError:
        raise Http404("Invalid date or time format")

    # Get the number of tables of selected size
    tables = [
        sub_facility.tables_of_1, sub_facility.tables_of_2, sub_facility.tables_of_3,
        sub_facility.tables_of_4, sub_facility.tables_of_5, sub_facility.tables_of_6,
        sub_facility.tables_of_7, sub_facility.tables_of_8, sub_facility.tables_of_9,
        sub_facility.tables_of_10, sub_facility.tables_of_11, sub_facility.tables_of_12
    ]
    selected_table_num = tables[people - 1]
    slot_length = datetime.timedelta(minutes=sub_facility.slot_length)

    # Determine the opening and closing times for the selected day of the week
    day_of_week = selected_date.weekday()
    if day_of_week == 0:
        opening_time = sub_facility.monday_open
        closing_time = sub_facility.monday_close
    elif day_of_week == 1:
        opening_time = sub_facility.tuesday_open
        closing_time = sub_facility.tuesday_close
    elif day_of_week == 2:
        opening_time = sub_facility.wednesday_open
        closing_time = sub_facility.wednesday_close
    elif day_of_week == 3:
        opening_time = sub_facility.thursday_open
        closing_time = sub_facility.thursday_close
    elif day_of_week == 4:
        opening_time = sub_facility.friday_open
        closing_time = sub_facility.friday_close
    elif day_of_week == 5:
        opening_time = sub_facility.saturday_open
        closing_time = sub_facility.saturday_close
    elif day_of_week == 6:
        opening_time = sub_facility.sunday_open
        closing_time = sub_facility.sunday_close

    # Verify that the selected time is within the operational hours
    if not (opening_time <= selected_time < closing_time):
        raise Http404("Selected time is outside of operational hours")

    if request.method == 'POST':
        try:
            with transaction.atomic():
                existing_bookings = RestaurantBooking.objects.filter(
                    restaurant_facility=sub_facility, date=selected_date, table_size=people
                ).select_for_update()

                tables_remaining = selected_table_num
                current_time = datetime.datetime.combine(selected_date, selected_time)

                for booking in existing_bookings:
                    booking_start = datetime.datetime.combine(selected_date, booking.time)
                    booking_end = booking_start + slot_length
                    if current_time < booking_end and (current_time + slot_length) > booking_start:
                        tables_remaining -= 1
                        if tables_remaining == 0:
                            break
                    elif booking.time == current_time:
                        tables_remaining -= 1
                        if tables_remaining == 0:
                            break

                if tables_remaining == 0:
                    raise Http404("You were pipped to the post! Someone else has booked this table")

                # Create the booking
                booking = RestaurantBooking(
                    user=request.user,
                    restaurant_facility=sub_facility,
                    date=selected_date,
                    time=selected_time,
                    paid=True,
                    table_size=people
                )
                booking.save()
                return redirect('/booking/success')
        except DatabaseError:
            raise Http404("An error occurred while trying to book the table. Please try again.")

    return render(request, 'restConfirmation.html', {
        'subfacility_id': restaurant_facility_id,
        'selected_date': selected_date,
        'selected_time': selected_time,
        'number_of_people': people
    })
                                    
                                    

@login_required_customer
def booking_success(request):
    return render(request, 'bookingSuccess.html')

@login_required_customer
def delete_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id, user=request.user)
    
    if request.method == 'POST':
        booking.delete()
        return redirect('/customer/home')  # Redirect to a page listing all bookings for the customer

    return render(request, 'delete_booking_confirmation.html', {'booking': booking})


@login_required_customer
def edit_booking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)
    
    # Verify that the booking belongs to the current user
    if booking.user != request.user and booking.sub_facility.facility.business != request.user.business_link.business:
        print(booking.user, request.user)
        print(booking)
        return redirect('/customer/home')  # Redirect to a booking list or an error page if needed

    sub_facility = booking.sub_facility
    facility = sub_facility.facility
    selected_date = booking.date

    # Get the selected date from the GET parameters, default to the booking date if not provided
    selected_date_str = request.GET.get('date', None)
    if selected_date_str:
        selected_date = parse_date(selected_date_str)
    else:
        selected_date = booking.date

    # Calculate available slots for the sub-facility
    closed_dates = CloseNormalFacility.objects.filter(normal_facility=sub_facility)
    slots = []
    if not closed_dates.filter(date=selected_date).exists():
        day_of_week = selected_date.weekday()
        opening_time, closing_time = get_opening_closing_times(sub_facility, day_of_week)

        # Calculate available slots for the sub-facility on the given date
        existing_bookings = Booking.objects.filter(sub_facility=sub_facility, date=selected_date)
        current_time = datetime.datetime.combine(selected_date, opening_time)
        end_time = datetime.datetime.combine(selected_date, closing_time)
        slot_frequency = datetime.timedelta(minutes=sub_facility.slot_frequency)

        while current_time < end_time:
            # Iterate through bookings to check for slot availability
            bookings_at_slot = 0
            for existing_booking in existing_bookings:
                booking_start = datetime.datetime.combine(selected_date, existing_booking.time)
                booking_end = booking_start + datetime.timedelta(minutes=sub_facility.slot_length)
                if current_time < booking_end and (current_time + datetime.timedelta(minutes=sub_facility.slot_length)) > booking_start:
                    bookings_at_slot += 1
            if bookings_at_slot < sub_facility.slot_quantity:
                slots.append(str(current_time.time()))
            current_time += slot_frequency

    if request.method == 'POST':
        if request.POST.get('type') == 'Confirm Time':
            new_date = request.POST.get('date')
            new_time = request.POST.get('time')

            # Convert new_date and new_time to datetime objects
            new_date_obj = parse_date(new_date)
            new_time_obj = datetime.datetime.strptime(new_time, '%H:%M:%S').time()

            # Check if the new slot is still available
            existing_bookings = Booking.objects.filter(sub_facility=sub_facility, date=new_date_obj)
            is_available = True
            for existing_booking in existing_bookings:
                booking_start = datetime.datetime.combine(new_date_obj, existing_booking.time)
                booking_end = booking_start + datetime.timedelta(minutes=sub_facility.slot_length)
                new_booking_start = datetime.datetime.combine(new_date_obj, new_time_obj)
                new_booking_end = new_booking_start + datetime.timedelta(minutes=sub_facility.slot_length)
                if new_booking_start < booking_end and new_booking_end > booking_start:
                    is_available = False
                    break

            if is_available:
                booking.date = new_date_obj
                booking.time = new_time_obj
                booking.save()

                # Verify the booking details after saving
                print(booking)
                print(request.user)
            else:
                # Handle the case where the slot is no longer available
                return render(request, 'edit_booking1.html', {
                    'booking': booking,
                    'facility': facility,
                    'sub_facility': sub_facility,
                    'slots': slots,
                    'selected_date': selected_date.strftime('%Y-%m-%d'),
                    'error_message': 'The selected slot is no longer available. Please choose another slot.'
                })
        
        elif request.POST.get('type') == 'Update Note':
            new_notes = request.POST.get('notes')
            booking.booking_notes = new_notes
            booking.save()

            print(booking)

        elif request.POST.get('type') == 'Confirm Status':
            temp = request.POST.get('paid') is not None  # Check if 'paid' checkbox is checked
            booking.paid = temp  # Update the booking's paid status
            booking.save()  # Save the booking with the new status

            print(booking)

        else:
            print("Invalid action")
            
        return redirect('/bookings/' + str(booking.id) + '/edit')  

    return render(request, 'edit_booking1.html', {
        'booking': booking,
        'facility': facility,
        'sub_facility': sub_facility,
        'slots': slots,
        'selected_date': selected_date.strftime('%Y-%m-%d')
    })

def get_opening_closing_times(sub_facility, day_of_week):
    if day_of_week == 0:
        return sub_facility.monday_open, sub_facility.monday_close
    elif day_of_week == 1:
        return sub_facility.tuesday_open, sub_facility.tuesday_close
    elif day_of_week == 2:
        return sub_facility.wednesday_open, sub_facility.wednesday_close
    elif day_of_week == 3:
        return sub_facility.thursday_open, sub_facility.thursday_close
    elif day_of_week == 4:
        return sub_facility.friday_open, sub_facility.friday_close
    elif day_of_week == 5:
        return sub_facility.saturday_open, sub_facility.saturday_close
    elif day_of_week == 6:
        return sub_facility.sunday_open, sub_facility.sunday_close
    return None, None



