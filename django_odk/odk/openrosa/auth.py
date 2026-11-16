# -*- coding: utf-8 -*-
"""
HTTP Basic authentication for OpenRosa endpoints (ODK Collect).

Enable with, in settings.py:
    ODK_SUBMISSION_AUTH = True
Then in ODK Collect: Settings > Project settings > Server > Username / Password.
Credentials are those of a Django user. Use HTTPS, Basic auth sends them in clear.
"""
import base64
import binascii
import logging
from functools import wraps

from django.conf import settings
from django.contrib.auth import authenticate
from django.http import HttpResponse

LOG = logging.getLogger(__name__)


def _unauthorized():
    response = HttpResponse("Authentication required", status=401)
    response['WWW-Authenticate'] = 'Basic realm="odk"'
    response['X-OpenRosa-Version'] = '1.0'
    return response


def _basic_auth_user(request):
    header = request.META.get('HTTP_AUTHORIZATION', '')
    scheme, _, credentials = header.partition(' ')
    if scheme.lower() != 'basic' or not credentials:
        return None
    try:
        decoded = base64.b64decode(credentials.strip(), validate=True).decode('utf-8')
    except (binascii.Error, UnicodeDecodeError):
        return None
    username, sep, password = decoded.partition(':')
    if not sep:
        return None
    user = authenticate(request, username=username, password=password)
    if user is None or not user.is_active:
        LOG.warning("ODK Basic auth failed for username=%r", username)
        return None
    return user


def openrosa_basic_auth(view_func):
    """
    Require HTTP Basic auth when settings.ODK_SUBMISSION_AUTH is True.
    An already logged-in session user is accepted too.
    """
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if getattr(settings, 'ODK_SUBMISSION_AUTH', False):
            if not request.user.is_authenticated:
                user = _basic_auth_user(request)
                if user is None:
                    return _unauthorized()
                request.user = user
        return view_func(request, *args, **kwargs)
    return wrapper
