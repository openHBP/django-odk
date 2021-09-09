# -*- coding: utf-8 -*-
import logging
from datetime import datetime
from django.utils.formats import get_format
from django.core import mail
from django.core.mail import get_connection
from django.db import connection
from .settings import EMAIL_BACKEND, PROJECT_NAME


__author__ = 'Patrick HOUBEN'
__email__ = 'p.houben@cra.wallonie.be'
__copyright__ = 'Copyright 2019, Patrick HOUBEN'
__license__ = 'GPLv3'
__date__ = '2019-01-18'
__version__ = '0.1'
__status__ = 'Development'


# copied from view_breadcrumbs
def get_app_name(model):
    if model._meta.installed:
        return getattr(model._meta, 'label', '.').split('.')

    raise AppRegistryNotReady(
        '{model} is not installed or missing from the app registry.'.format(
            model=getattr(model._meta, 'app_label', model.__class__.__name__)
        )
    )


def parse_date(date_str):
    """
    https://stackoverflow.com/questions/22918095/django-string-to-date-format
    Parse date from string by DATE_INPUT_FORMATS of current language
    """
    for item in get_format('DATE_INPUT_FORMATS'):
        try:
            return datetime.strptime(date_str, item).date()
        except (ValueError, TypeError):
            continue
    return None


class MailingAdmins(logging.Handler):
    """
    Simple email to Admins, inspired from django.utils.log.AdminEmailHandler
    """
    subject = "{0}: SERVER ERROR 500".format(PROJECT_NAME)

    def __init__(self, subject=subject, user=None):
        super().__init__()
        self.subject = subject
        self.user = user

    def emit(self, record):
        # if user passed as extra: logger.error(msg, extra={'user': request.user})
        # but passed in msg
        self.subject += ' | user: {0}'.format(record.user)
        self.send_mail(subject=self.subject,
                       message=self.format(record), fail_silently=True)

    def send_mail(self, subject, message, *args, **kwargs):
        mail.mail_admins(subject, message, *args,
                         connection=self.connection(), **kwargs)

    def connection(self):
        return get_connection(backend=EMAIL_BACKEND, fail_silently=True)


class UserLogFilter(logging.Filter):
    def filter(self, record):
        if not hasattr(record, 'user'):
            record.user = '--'
        return True
