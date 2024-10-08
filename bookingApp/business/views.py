# views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth import logout, login, authenticate
from django.http import Http404
from .forms import *
from .models import *
from .decorators import login_required_customer, login_required_business
from datetime import date, datetime, timedelta
from customer.models import Booking, Customer
from customer.forms import BookingFormBusiness
from customer.views import send_activation_email, generate_activation_code
from django.contrib import messages
from customer.forms import ActivationForm
from django.views.decorators.clickjacking import xframe_options_exempt
from django.contrib.auth import update_session_auth_hash


"""
View for landing page on my site.
"""
@xframe_options_exempt
def landing(request):
    return render(request, "landing.html", {})



"""
View to create an account for a business.
"""
def authViewBusiness(request):
    if request.method == "POST":
        form = BusinessSignupForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.is_staff = False
            user.save()
            
            # Create a Customer record
            customer = Customer(
                user=user,
                phone_number=form.cleaned_data.get('phone_number', ''),
                address=form.cleaned_data.get('address', ''),
                activation_code=generate_activation_code(),
                is_active=False
            )
            customer.save()
            
            # Send activation email
            send_activation_email(user)
            
            return redirect("/signup/business/login")
    else:
        form = BusinessSignupForm()
    
    return render(request, "signup.html", {"form": form})


"""
View to activate/verify the email of an account.
"""
@login_required_business
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


"""
View to login a business during business creation
"""
def loginViewBusiness(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/signup/business/create")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


"""
View to create a business
"""
@login_required_business
def createNewBusiness(request):
    if request.method == 'POST':
        form = BusinessForm(request.POST)
        if form.is_valid():
            business = form.save()
            # Check if the user is already linked to another business
            if not hasattr(request.user, 'business_link'):
                UserBusinessLink.objects.create(user=request.user, business=business, userType='staff')
                return redirect('/business/dashboard')  # Redirect to a success page or business list page
            else:
                form.add_error(None, "You are already linked to another business.")
    else:
        form = BusinessForm()
    return render(request, 'createBusiness.html', {'form': form})


"""
View to log into business once business has been created
"""
def loginBusiness(request):
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            username = form.cleaned_data['username']
            password = form.cleaned_data['password']
            user = authenticate(request, username=username, password=password)
            if user is not None:
                login(request, user)
                return redirect("/business/dashboard")
            else:
                form.add_error(None, "Invalid username or password.")
    else:
        form = LoginForm()
    return render(request, "login.html", {"form": form})


"""
View to see the business dashboard
"""
@login_required_business
def businessDashboard(request):
    # Check if the user is staff
    try:
        business_link = request.user.business_link
        business = business_link.business
    except UserBusinessLink.DoesNotExist:
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not linked to any business
    except UserBusinessLink.MultipleObjectsReturned:
        return redirect('/access_denied')  # Redirect to an access denied page if the user is linked to multiple businesses
    
    # check if the user has verified their email
    if not request.user.customer.is_active:
        return redirect('/activate-account')

    # Check if the userType is 'staff' in the UserBusinessLink model
    if business_link.userType != 'staff':
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff
    
    # Retrieve the facilities associated with the business
    facilities = Facility.objects.filter(business=business)

    return render(request, 'businessDashboard.html', {'business': business, 'facilities': facilities})


"""
View to log out user from site
"""
def myLogout(request):
    logout(request)
    return redirect("/")


"""
View to show that access has been denied
"""
def accessDenied(request):
    return render(request, 'accessDenied.html')


"""
View to create a new facility
"""
@login_required_business
def newFacility(request):
    try:
        # Get the business linked to the logged-in user
        business_link = request.user.business_link
        business = business_link.business
    except UserBusinessLink.DoesNotExist:
        return redirect('access_denied')
    

    if request.method == 'POST':
        form = FacilityForm(request.POST, business=business)
        if form.is_valid():
            facility = form.save(commit=False)
            facility.business = business
            facility.save()
            return redirect('/business/dashboard')  # Redirect to a success page or business list page
    else:
        form = FacilityForm(business=business)
    return render(request, 'newFacility.html', {'form': form})


"""
View to show information on each facility
"""
@login_required_business
def facility_detail(request, facility_id):
    try:
        business_link = request.user.business_link
        business = business_link.business

        # Retrieve the facility
        facility = Facility.objects.get(id=facility_id)

        # Check if the facility belongs to the business
        if facility.business != business:
            raise Http404("Facility not found")  # Facility does not belong to the user's business

        # Check if the user is staff
        if business_link.userType != 'staff':
            return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

        if facility.facilityType == 'Sports' or facility.facilityType == 'Generic':
            subFacilities = NormalFacility.objects.filter(facility=facility)
        elif facility.facilityType == 'Restaurant':
            subFacilities = RestaurantFacility.objects.filter(facility=facility)

        # Render the facility detail page
        return render(request, 'facilityDetail.html', {'facility': facility,'subFacilities': subFacilities})
    
    except UserBusinessLink.DoesNotExist:
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not linked to any business
    
    except UserBusinessLink.MultipleObjectsReturned:
        return redirect('/access_denied')  # Redirect to an access denied page if the user is linked to multiple businesses
    
    except Facility.DoesNotExist:
        raise Http404("Facility not found")  # Facility does not exist     


"""
View to create a new sub-facility
"""
@login_required_business
def newSubFacility(request, facility_id):
    
    try:
        business_link = request.user.business_link
        business = business_link.business

        # Retrieve the facility
        facility = Facility.objects.get(id=facility_id)

        # Check if the facility belongs to the business
        if facility.business != business:
            raise Http404("Facility not found")  # Facility does not belong to the user's business

        # Check if the user is staff
        if business_link.userType != 'staff':
            return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

        # Determine the type of facility to create based on the facilityType of the parent facility
        if facility.facilityType == 'Sports' or facility.facilityType == 'Generic':
            # Create a form for NormalFacility
            form = NormalFacilityForm(request.POST or None, business=business)
        elif facility.facilityType == 'Restaurant':
            # Create a form for RestaurantFacility
            form = RestaurantFacilityForm(request.POST or None, business=business)
        else:
            # Facility type not supported
            raise Http404("Unsupported facility type")

        # If the form is submitted and valid, save the sub-facility
        if request.method == 'POST':
            if form.is_valid():
                sub_facility = form.save(commit=False)
                sub_facility.facility = facility
                sub_facility.save()
                redirectString = '/facilities/' + str(facility_id)
                return redirect(redirectString)  # Redirect to a success URL after saving the sub-facility

        # Render the template with the form
        return render(request, 'newSubFacility.html', {'facility': facility, 'form': form})

    except Facility.DoesNotExist:
        raise Http404("Facility not found")
    except Exception as e:
        print(e)  # Log the exception for debugging purposes
        return redirect('/access_denied')


"""
View to delete a facility object (Can contain many sub Facilities).
"""
@login_required_business
def deleteFacilityGroup(request, facility_id):
    try:
        business_link = request.user.business_link
        business = business_link.business

        # Retrieve the facility
        facility = get_object_or_404(Facility, id=facility_id)

        # Check if the facility belongs to the business
        if facility.business != business:
            raise Http404("Facility not found")  # Facility does not belong to the user's business

        # Check if the user is staff
        if business_link.userType != 'staff':
            return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

        if request.method == 'POST':
            form = ConfirmDeleteForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                user = authenticate(username=request.user.username, password=password)
                if user is not None:
                    # Password is correct, delete the facility
                    facility.delete()
                    return redirect('/business/dashboard')
                else:
                    form.add_error('password', 'Incorrect password.')
        else:
            form = ConfirmDeleteForm()

        return render(request, 'confirm_delete_facility.html', {'form': form, 'facility': facility})

    except Facility.DoesNotExist:
        raise Http404("Facility not found")
    except Exception as e:
        print(e)
        raise Http404("An error occurred")
    

"""
View to delete a normalFacility (This is an actual facility which can be booked).
"""
@login_required_business
def deleteNormalFacility(request, facility_id):
    try:
        business_link = request.user.business_link
        business = business_link.business

        # Retrieve the normal facility
        normal_facility = get_object_or_404(NormalFacility, id=facility_id)

        # Check if the normal facility belongs to the business
        if normal_facility.facility.business != business:
            raise Http404("Facility not found")  # NormalFacility does not belong to the user's business

        # Check if the user is staff
        if business_link.userType != 'staff':
            return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

        if request.method == 'POST':
            form = ConfirmDeleteForm(request.POST)
            if form.is_valid():
                password = form.cleaned_data['password']
                user = authenticate(username=request.user.username, password=password)
                if user is not None:
                    # Password is correct, delete the normal facility
                    normal_facility.delete()
                    return redirect('/business/dashboard')
                else:
                    form.add_error('password', 'Incorrect password.')
        else:
            form = ConfirmDeleteForm()

        return render(request, 'confirm_delete_normal_facility.html', {'form': form, 'normal_facility': normal_facility})

    except NormalFacility.DoesNotExist:
        raise Http404("Facility not found")
    except Exception as e:
        print(e)
        raise Http404("An error occurred")   
    

"""
View to edit a normalFacility. (This can include opening times, price, slot length, etc.)
"""
@login_required_business
def editFacility(request, facility_id):
    
    business_link = request.user.business_link
    business = business_link.business

    # Retrieve the normal facility
    normal_facility = get_object_or_404(NormalFacility, id=facility_id)

    # Check if the normal facility belongs to the business
    if normal_facility.facility.business != business:
        raise Http404("Facility not found")  # NormalFacility does not belong to the user's business

    # Check if the user is staff
    if business_link.userType != 'staff':
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff
    
    if request.method == 'POST':
        form = NormalFacilityForm(request.POST, instance=normal_facility, business=request.user.business_link.business)
        if form.is_valid():
            form.save()
            return redirect('/business/dashboard')  # Redirect to dashboard or another appropriate page after editing
    else:
        form = NormalFacilityForm(instance=normal_facility, business=request.user.business_link.business)

    return render(request, 'edit_facility.html', {'form': form, 'facility': normal_facility})


"""
View to delete a restaurant facility. NOTE - Not included in the final product.
"""
@login_required_business
def deleteRestFacility(request, facility_id):
    business_link = request.user.business_link
    business = business_link.business

    # Retrieve the restaurant facility
    restaurant_facility = get_object_or_404(RestaurantFacility, id=facility_id)

    # Check if the facility belongs to the business
    if restaurant_facility.facility.business != business:
        raise Http404("Facility not found")  # Facility does not belong to the user's business

    # Check if the user is staff
    if business_link.userType != 'staff':
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

    if request.method == 'POST':
        form = ConfirmDeleteForm(request.POST)
        if form.is_valid():
            password = form.cleaned_data['password']
            user = authenticate(username=request.user.username, password=password)
            if user is not None:
                # Password is correct, delete the facility
                restaurant_facility.delete()
                return redirect('/business/dashboard')
            else:
                form.add_error('password', 'Incorrect password.')
    else:
        form = ConfirmDeleteForm()

    return render(request, 'confirm_delete_restaurant_facility.html', {'form': form, 'facility': restaurant_facility})


"""
View to edit a restaurantFacility. NOTE - Not included in the final product.
"""
@login_required_business
def editRestFacility(request, facility_id):
    business_link = request.user.business_link
    business = business_link.business

    # Retrieve the restaurant facility
    restaurant_facility = get_object_or_404(RestaurantFacility, id=facility_id)

    # Check if the facility belongs to the business
    if restaurant_facility.facility.business != business:
        raise Http404("Facility not found")  # Facility does not belong to the user's business

    # Check if the user is staff
    if business_link.userType != 'staff':
        return redirect('/access_denied')  # Redirect to an access denied page if the user is not staff

    if request.method == 'POST':
        form = RestaurantFacilityForm(request.POST, instance=restaurant_facility, business=business)
        if form.is_valid():
            form.save()
            return redirect('/business/dashboard')  # Redirect to dashboard or another appropriate page after editing
    else:
        form = RestaurantFacilityForm(instance=restaurant_facility, business=business)

    return render(request, 'edit_restaurant_facility.html', {'form': form, 'facility': restaurant_facility})


"""
View to close a normalFacility for a day. This means no bookings for this day can be made.
"""
@login_required_business
def closeFacility(request, facility_id):
    facility = get_object_or_404(NormalFacility, id=facility_id)

    # Check that the facility belongs to the logged-in user
    if facility.facility.business != request.user.business_link.business:
        raise Http404("Naughty naughty! You shouldn't be playing with the URL ;)")

    # Get all the dates already closed for this facility
    today = date.today()
    closed_dates = CloseNormalFacility.objects.filter(normal_facility=facility, date__gte=today).order_by('date')
    closed_dates_list = [closed_date.date for closed_date in closed_dates]

    if request.method == 'POST':
        form = CloseNormalFacilityForm(request.POST)
        if form.is_valid():
            # Validate the password
            password = form.cleaned_data.get('password')
            user = authenticate(username=request.user.username, password=password)
            if user is None:
                form.add_error('password', 'Invalid password')

            else:
                # Get the instance of the form without saving it yet
                closed_facility = form.save(commit=False)
                
                # Set the normal_facility field manually
                closed_facility.normal_facility = facility

                if closed_facility.date in closed_dates_list:
                    form.add_error('date', 'Facility already closed on this date')
                    return render(request, 'close_normal_facility.html', {
                        'form': form, 
                        'facility': facility, 
                        'closed_dates': closed_dates
                    })
                
                # Save the instance with the updated normal_facility field
                closed_facility.save()
                return redirect(request.path_info)
    else:
        form = CloseNormalFacilityForm(initial={'normal_facility': facility})

    return render(request, 'close_normal_facility.html', {
        'form': form, 
        'facility': facility, 
        'closed_dates': closed_dates
    })


"""
View to reopen a normalFacility on a day where it has been closed.
"""
@login_required_business
def openFacility(request, facility_id, selected_date):
    facility = get_object_or_404(NormalFacility, id=facility_id)

    # Validate that the facility belongs to the logged-in user
    if facility.facility.business != request.user.business_link.business:
        raise Http404("Naughty naughty! You shouldn't be playing with the URL ;)")

    # Convert the selected_date to a date object
    try:
        selected_date = datetime.strptime(selected_date, "%Y-%m-%d").date()
    except ValueError:
        raise Http404("Invalid date format")

    # Find all closed facility instances for the selected date
    closed_facilities = CloseNormalFacility.objects.filter(normal_facility=facility, date=selected_date)

    if request.method == 'POST':
        # Delete all instances of closed_facilities
        closed_facilities.delete()
        return redirect('/facility/normal/close/' + str(facility_id))  # Adjust the redirect to your actual dashboard URL

    return render(request, 'confirm_reopen.html', {'facility': facility, 'closed_date': selected_date})


"""
View to show a business all the bookings for a selected normalFacility.
"""
@login_required_business
def facilityBookings(request, facility_id):
    facility = get_object_or_404(NormalFacility, id=facility_id)

    # Check that the facility belongs to the logged-in user
    if facility.facility.business != request.user.business_link.business:
        raise Http404("Naughty naughty! You shouldn't be playing with the URL ;)")

    # Get all the bookings for this facility
    bookings = Booking.objects.filter(sub_facility=facility).order_by('date', 'time')

   # Calculate end time for each booking
    booking_details = []
    for booking in bookings:
        start_datetime = datetime.combine(booking.date, booking.time)
        end_datetime = start_datetime + timedelta(minutes=facility.slot_length)
        booking_details.append({
            'id': booking.id,
            'username': booking.user.username if booking.user else booking.name,
            'date': booking.date,
            'start_time': booking.time,
            'end_time': end_datetime.time(),
            'notes': booking.booking_notes,
            'paid': booking.paid
        })

    return render(request, 'facility_bookings.html', {'facility': facility, 'bookings': booking_details})


"""
View to look at the details of a specific booking.
"""
@login_required_business
def viewBooking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check that the booking belongs to the logged-in user
    if booking.sub_facility.facility.business != request.user.business_link.business:
        raise Http404("Naughty naughty! You shouldn't be playing with the URL ;)")

    # Calculate end time for the booking
    start_datetime = datetime.combine(booking.date, booking.time)
    end_datetime = start_datetime + timedelta(minutes=booking.sub_facility.slot_length)

    return render(request, 'view_booking.html', {
        'booking': booking,
        'start_time': booking.time,
        'end_time': end_datetime.time(),
        'user': request.user
    })


"""
View to delete a booking.
"""
@login_required_business
def deleteBooking(request, booking_id):
    booking = get_object_or_404(Booking, id=booking_id)

    # Check that the booking belongs to the logged-in user
    if booking.sub_facility.facility.business != request.user.business_link.business:
        raise Http404("Naughty naughty! You shouldn't be playing with the URL ;)")

    if request.method == 'POST':
        booking.delete()
        return redirect('/facility/normal/bookings/' + str(booking.sub_facility.id))  # Adjust the redirect to your actual dashboard URL

    return render(request, 'delete_booking.html', {'booking': booking})


"""
View to edit booking. Redirects to another view in the customer app where the edit can be made.
"""
@login_required_business
def editBooking(request, booking_id):
    return redirect('/bookings/' + str(booking_id) + '/edit')  # Adjust the redirect to your actual dashboard URL


"""
View for a page where user can enter their stripe keys to they can accpet payments. The secret key is encrypted in the database.
"""
@login_required_business
def manage_stripe_keys(request):
    # Get the current user's business
    try:
        business = request.user.business_link.business
    except Business.DoesNotExist:
        messages.error(request, "You don't have a business associated with your account.")
        return redirect('/')  # Redirect to a suitable page

    # Try to get existing StripeKey object, or create a new one
    stripe_key = StripeKey.objects.filter(business=business).first()

    if request.method == 'POST':
        form = StripeKeyForm(request.POST, instance=stripe_key, business=business)
        if form.is_valid():
            stripe_key = form.save(commit=False)
            stripe_key.business = business
            stripe_key.save()
            messages.success(request, "Your Stripe keys have been successfully updated.")
            return redirect('/business/dashboard')  # Redirect to a suitable page
    else:
        form = StripeKeyForm(instance=stripe_key, business=business)

    return render(request, 'manage_stripe_keys.html', {'form': form})


"""
View to change details of the business user's account. NOTE - This code doesn't work and is not used. The next views cover this.
"""
@login_required_business
def account_settings(request):
    business = request.user.business_link.business

    # Initialize all forms
    email_form = ChangeEmailForm(user=request.user, business=business)
    master_password_form = ChangeMasterPasswordForm(business=business)
    account_password_form = ChangeAccountPasswordForm(user=request.user, business=business)
    business_details_form = UpdateBusinessDetailsForm(instance=business, business=business)

    if request.method == 'POST':
        # Check which form was submitted and process accordingly
        if 'email_form' in request.POST:
            email_form = ChangeEmailForm(request.POST, user=request.user, business=business)
            if email_form.is_valid():
                email_form.save()
                return redirect('/update/business')

        elif 'master_password_form' in request.POST:
            master_password_form = ChangeMasterPasswordForm(request.POST, business=business)
            if master_password_form.is_valid():
                master_password_form.save()
                return redirect('/update/business')

        elif 'account_password_form' in request.POST:
            account_password_form = ChangeAccountPasswordForm(user=request.user, data=request.POST, business=business)
            if account_password_form.is_valid():
                account_password_form.save()
                return redirect('/update/business')

        elif 'business_details_form' in request.POST:
            business_details_form = UpdateBusinessDetailsForm(request.POST, instance=business, business=business)
            if business_details_form.is_valid():
                business_details_form.save()
                return redirect('/update/business')

    context = {
        'email_form': email_form,
        'master_password_form': master_password_form,
        'account_password_form': account_password_form,
        'business_details_form': business_details_form
    }
    return render(request, 'account_settings.html', context)


"""
View to change the details of the business. E.g. Name, and description.
"""
@login_required_business
def update_business_details(request):
    business = request.user.business_link.business

    if request.method == 'POST':
        form = UpdateBusinessDetailsForm(request.POST, instance=business, business=business)
        if form.is_valid():
            form.save()
            return redirect('/update/business')  # Redirect to the same page or another success page
    else:
        form = UpdateBusinessDetailsForm(instance=business, business=business)

    context = {
        'form': form,
    }
    return render(request, 'update_business_details.html', context)


"""
View to change the accounts password to log in.
"""
@login_required_business
def change_account_password(request):
    business = request.user.business_link.business

    if request.method == 'POST':
        form = ChangeAccountPasswordForm(request.POST, business=business, user=request.user)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)  # Important to keep the user logged in
            return redirect('/update/business')  # Redirect after successful password change
    else:
        form = ChangeAccountPasswordForm(business=business, user=request.user)

    context = {
        'form': form,
    }
    return render(request, 'change_account_password.html', context)


"""
View to change the accounts master password. Different to acount password. This password allows the user to make changes to the business.
"""
@login_required_business
def change_master_password(request):
    business = request.user.business_link.business

    if request.method == 'POST':
        form = ChangeMasterPasswordForm(request.POST, instance=business)
        if form.is_valid():
            form.save()
            return redirect('/update/business')  # Redirect to the profile or another success page
    else:
        form = ChangeMasterPasswordForm(instance=business)

    context = {
        'form': form,
    }
    return render(request, 'change_master_password1.html', context)


"""
View to change the accounts email adress.
"""
@login_required_business
def change_email(request):
    business = request.user.business_link.business

    if request.method == 'POST':
        form = ChangeEmailForm(request.POST, user=request.user, business=business)
        if form.is_valid():
            # Save the new email address
            form.save()
            return redirect('/update/business')  # Redirect to the profile or another success page
    else:
        form = ChangeEmailForm(user=request.user, business=business)

    context = {
        'form': form,
    }
    return render(request, 'change_email.html', context)


"""
This is a view to a simple webpage which redirects the user to one of the previous 4 views to make changes to their account.
"""
@login_required_business
def choose_change(request):
    return render(request, 'choose_change.html')
