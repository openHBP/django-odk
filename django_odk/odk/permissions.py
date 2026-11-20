# -*- coding: utf-8 -*-
"""
Server-side authorization for the django-odk management views.

A user is allowed an action when he is authenticated AND one of:
  - is_superuser
  - has a truthy `is_odk_admin` attribute/property/method (host project role)
  - holds the Django model permission (e.g. 'odk.delete_xformsubmit'),
    grantable from the admin through users/groups.
"""
from functools import wraps

from django.contrib.auth.mixins import PermissionRequiredMixin
from django.contrib.auth.views import redirect_to_login
from django.core.exceptions import PermissionDenied


def is_odk_admin(user):
    if not user.is_authenticated or not user.is_active:
        return False
    if user.is_superuser:
        return True
    flag = getattr(user, 'is_odk_admin', False)
    if callable(flag):
        flag = flag()
    return bool(flag)


def user_has_odk_perm(user, perm):
    """perm: a 'app_label.codename' string, or None for 'superuser only'."""
    if not user.is_authenticated or not user.is_active:
        return False
    if perm is None:
        return user.is_superuser
    return is_odk_admin(user) or user.has_perm(perm)


class OdkPermissionMixin(PermissionRequiredMixin):
    """
    Anonymous -> redirect to login, authenticated without permission -> 403.
    Set `permission_required` on the view (single 'app.codename' string).
    """
    def has_permission(self):
        return user_has_odk_perm(self.request.user, self.permission_required)

    def get_permission_required(self):
        # PermissionRequiredMixin requires a non-empty value; superuser-only
        # views (permission_required=None) are handled by has_permission.
        return (self.permission_required,) if self.permission_required else ()


def odk_permission_required(perm, login_url='admin:login'):
    """Function-view equivalent of OdkPermissionMixin."""
    def decorator(view_func):
        @wraps(view_func)
        def wrapper(request, *args, **kwargs):
            if not request.user.is_authenticated:
                return redirect_to_login(request.get_full_path(), login_url)
            if not user_has_odk_perm(request.user, perm):
                raise PermissionDenied
            return view_func(request, *args, **kwargs)
        return wrapper
    return decorator


def check_odk_perm(request, perm):
    """Inline check for side-effect actions routed through a detail view."""
    if not user_has_odk_perm(request.user, perm):
        raise PermissionDenied
