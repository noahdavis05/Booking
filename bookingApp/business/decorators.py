# your_app/decorators.py
from functools import wraps
from django.shortcuts import redirect
from django.conf import settings

"""
These two functions are used similarly to @login_required.
But means you can redirect to the user login and the business login pages, instead of only being able to redirect to one of them.
"""


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
