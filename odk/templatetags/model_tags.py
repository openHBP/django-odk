# -*- coding: utf-8 -*-
"""
If needed Copy/Paste this part into your own templatetags file
"""
import logging
from django import template
from django.db.models.query import QuerySet

register = template.Library()

__author__ = 'hbp'
__email__ = 'p.houben@cra.wallonie.be'
__copyright__ = 'Copyright 2021, Patrick Houben'
__license__ = 'GPLv3'
__date__ = '2021-07-07'
__version__ = '1.0'
__status__ = 'Development'

LOG = logging.getLogger(__name__)


@register.simple_tag
def get_verbose_field_name(objname, field_name):
    """
    Returns verbose_name for a field.
    """
    # Check wether objname is a QuerySet of directly the object instance!
    # QuerySet option should not be used since we do first() for each call in header
    if isinstance(objname, QuerySet):
        objcopy = objname
        instance = objcopy.first()
    else:
        instance = objname
    fname = instance._meta.get_field(field_name).verbose_name
    return fname.capitalize()