# -*- coding: utf-8 -*-
"""
odk.admin description
"""
from django.contrib import admin
from .models import XForm, XFormSubmit


class XFormAdmin(admin.ModelAdmin):
    list_display = ('form_id', 'version', 'xml_file')
    list_filter = ('xml_file',)
    search_fields = ('xml_file', 'xml_content', 'short_desc', 'title',)
    fields = ['xls_file', 'xml_file', 'short_desc', 'created_by', 'modified_by']


class XFormSubmitAdmin(admin.ModelAdmin):
    list_display = ( 'form_id', 'version', 'xml_file')
    list_filter = ('form_id', 'survey_date')
    search_fields = ('xml_file', 'xml_content', 'title',)
    fields = ['xml_file', 'picture_files']


admin.site.register(XForm, XFormAdmin)
admin.site.register(XFormSubmit)