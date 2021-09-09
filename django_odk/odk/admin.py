# -*- coding: utf-8 -*-
"""
odk.admin description
"""
from django.contrib import admin
from .models import XForm, XFormSubmit

admin.site.register(XForm)

admin.site.register(XFormSubmit)