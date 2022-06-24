# -*- coding: utf-8 -*-
"""
odk.admin description
"""
from django.contrib import admin
from django.contrib import messages
from django.utils.translation import gettext as _
from django.utils.timezone import now

from .models import XForm, XFormSubmit
from odkdata.utils import rm_digit, convert2camelcase
from odkdata import create_model, load_submit_data


##################
# XForm
##################
@admin.action(description=_('Convert XLSX to XML'))
def xform_convert(modeladmin, request, queryset):
    if queryset.count() > 1:
        messages.warning(request, "Please select record to process 1 by 1", fail_silently=True)
        return
    else:
        record = queryset.first()
        record.process_xform()
        record.save()


@admin.action(description=_('Create Model in odkdata'))
def xform_createmodel(modeladmin, request, queryset):
    """
    TODO
    must use overwrite_storage in admin otherwise filename get HEX extension!
    and odkdata.create_model.xls2django generate bad initial model name
    """
    if queryset.count() > 1:
        messages.warning(request, _("Please select 1 record at a time."), fail_silently=True)
        return
    else:
        record = queryset.first()
        if create_model.process(record):
            messages.success(request, "Model created")
            record.model_created_on = now()
            record.save()
        else:
            messages.error(request, _("Error while creating model."))


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
def xformsubmit_error(return_value, message, request, table_name):
    """Use only if return_value < 0"""
    if return_value == -1:
        messages.error(request, message)
        messages.info(request, "Did you create the model from 'Available form' menu or Admin?")
        messages.info(request, "After 'pip install django-odk' need to stop-start wsgi or gunicorn instead of restart")
    elif return_value == -2:
        messages.error(request, f"'odkdata_{table_name}' table does not exist in the database")
        messages.info(request, "Did you run 'manage.py makemigrations odkdata' then 'manage.py migrate'?")


def xformsubmit_return_message(ok_list, ko_list, message, request, table_name):
    if ok_list:
        messages.success(request, f"id {ok_list} loaded with success!")
    if ko_list:
        messages.error(request, message)
        messages.error(request, f"id {ko_list} error - check error logs - correct xml_content")



@admin.action(description=_('Insert in odkdata model'))
def xformsubmit_load_data(modeladmin, request, queryset):
    ok_list = []
    ko_list = []
    nbr = 0
    for obj in queryset:
        nbr += 1
        if nbr == 1:
            table_name = convert2camelcase(rm_digit(obj.form_id)).lower()

        return_value, message = load_submit_data.load_record(obj)
        
        # return_value < 0 => major issue stop loop
        if return_value < 0:
            xformsubmit_error(return_value, message, request, table_name)
            break
        
        # return_value 0 (error ko) or 1 (ok)
        if return_value == 1:
            ok_list.append(obj.id)
            obj.inserted_on = now()
            obj.save()
        else:
            ko_list.append(obj.id)


    xformsubmit_return_message(ok_list, ko_list, message, request, table_name)



class XFormSubmitAdmin(admin.ModelAdmin):
    list_display = ('id', 'form_id', 'version', 'xml_file', 'inserted_on', 'picture_files')
    list_filter = ('form_id', 'survey_date')
    search_fields = ('xml_file', 'xml_content', 'title',)
    # fields = ['xml_file', 'picture_files']
    actions = [xformsubmit_load_data]



admin.site.register(XForm, XFormAdmin)
admin.site.register(XFormSubmit, XFormSubmitAdmin)