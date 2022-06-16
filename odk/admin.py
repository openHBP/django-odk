# -*- coding: utf-8 -*-
"""
odk.admin description
"""
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext as _
from django.shortcuts import render

from .models import XForm, XFormSubmit
from .utils import ManageFile



@admin.action(description='Convert xlsx to xml')
def xform_convert(modeladmin, request, queryset):
    manage_file = ManageFile(request)
    if queryset.count() > 1:
        messages.warning(request, "Please select record to process 1 by 1", fail_silently=True)
        return
    else:
        record = queryset.first()
        record.process_xform()
        record.save()


class XFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'xls_file', 'form_id', 'version', 'xml_file')
    list_filter = ('xls_file',)
    search_fields = ('xls_file', 'xml_content', 'short_desc', 'title',)
    fields = ['xls_file', 'short_desc']
    actions = [xform_convert]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)    


class XFormSubmitAdmin(admin.ModelAdmin):
    list_display = ( 'form_id', 'version', 'xml_file')
    list_filter = ('form_id', 'survey_date')
    search_fields = ('xml_file', 'xml_content', 'title',)
    fields = ['xml_file', 'picture_files']


admin.site.register(XForm, XFormAdmin)
admin.site.register(XFormSubmit)