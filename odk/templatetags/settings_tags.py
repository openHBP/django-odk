# -*- coding: utf-8 -*-
"""
source.cms_pages.templatetags.settings_value description
"""
from django import template
from config import settings

register = template.Library()

# settings value
@register.simple_tag
def settings_value(name):
    allowed_keys = ('APP_VERSION',
                    'AVAILABLE_TXT',
                    'SUBMITTED_TXT',
                    'BASE_URL',
                    'LANGUAGES',
                    'TIME_ZONE',
                    'LOCAL_TIMEZONE',
                    'TERMS_OF_SERVICE',
                    )
    if name in allowed_keys:
        return getattr(settings, name, "")
    
    return ''
