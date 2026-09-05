from functools import wraps
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def company_staff_required(view_func):
    """
    Only Django staff accounts (created via the admin, per the project brief —
    there is no public registration path for the company role) may reach the
    company portal views this wraps.
    """
    @wraps(view_func)
    def _wrapped(request, *args, **kwargs):
        if not request.user.is_authenticated:
            return redirect_to_login(request.get_full_path(), login_url="company:login")
        if not request.user.is_staff:
            raise PermissionDenied("Company access only.")
        return view_func(request, *args, **kwargs)
    return _wrapped
