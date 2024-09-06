# your_app/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

def login_required_customer(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL_CUSTOMER)
    return _wrapped_view

def login_required_business(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        if request.user.is_authenticated:
            return view_func(request, *args, **kwargs)
        else:
            return redirect(settings.LOGIN_URL_BUSINESS)
    return _wrapped_view
