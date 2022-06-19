# -*- coding: utf-8 -*-
"""
odk.admin description
"""
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.shortcuts import render

from .models import XForm, XFormSubmit
from odkdata import create_model, load_submit_data


##################
# XForm
##################
@admin.action(description='Convert XLSX to XML')
def xform_convert(modeladmin, request, queryset):
    if queryset.count() > 1:
        messages.warning(request, "Please select record to process 1 by 1", fail_silently=True)
        return
    else:
        record = queryset.first()
        record.process_xform()
        record.save()


@admin.action(description='Create Model in odkdata')
def xform_createmodel(modeladmin, request, queryset):
    """
    TODO
    must use overwrite_storage in admin otherwise filename get HEX extension!
    and odkdata.create_model.xls2django generate bad initial model name
    """
    if queryset.count() > 1:
        messages.warning(request, "Please select record to process 1 by 1", fail_silently=True)
        return
    else:
        record = queryset.first()
        if create_model.process(record):
            messages.success(request, "Model created")
            record.model_created_on = now()
            record.save()
        else:
            messages.error(request, "Error while creating model")


class XFormAdmin(admin.ModelAdmin):
    list_display = ('id', 'xls_file', 'form_id', 'version', 'xml_file')
    list_filter = ('xls_file',)
    search_fields = ('xls_file', 'xml_content', 'short_desc', 'title',)
    # fields = ['xls_file', 'xml_content', 'short_desc', 'model_created']
    actions = [xform_convert, xform_createmodel]

    def save_model(self, request, obj, form, change):
        obj.created_by = request.user
        super().save_model(request, obj, form, change)    


##################
# XFormSubmit
##################

@admin.action(description='Load Submitted Data')
def xformsubmit_load_data(modeladmin, request, queryset):
    for record in queryset:
        load_submit_data.load_record(record)
        record.inserted_on = now()
        record.save()


class XFormSubmitAdmin(admin.ModelAdmin):
    list_display = ( 'form_id', 'version', 'xml_file', 'picture_files')
    list_filter = ('form_id', 'survey_date')
    search_fields = ('xml_file', 'xml_content', 'title',)
    # fields = ['xml_file', 'picture_files']
    actions = [xformsubmit_load_data]



admin.site.register(XForm, XFormAdmin)
admin.site.register(XFormSubmit, XFormSubmitAdmin)