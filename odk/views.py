# -*- coding: utf-8 -*-
"""
odk.views description
"""
__author__ = 'hbp'
__email__ = 'p.houben@cra.wallonie.be'
__copyright__ = 'Copyright 2017, Patrick Houben'
__license__ = 'GPLv3'
__date__ = '2021-07-07'
__version__ = '1.0'
__status__ = 'Development'

import os
import logging
# from lxml import etree # pretty display XML (submit)
# with python 3.9 we can use => import xml.etree.ElementTree as ET
# https://stackoverflow.com/questions/749796/pretty-printing-xml-in-python

from braces.views import LoginRequiredMixin

from django.utils.translation import ugettext as _
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect

from .storage import overwrite_storage
from .models import XForm, XFormSubmit
from .forms import OdkForm
from .utils import ManageFile


LOG = logging.getLogger(__name__)
LOG_DEBUG = logging.getLogger("mydebug")


def home(request):
    title = _("Welcome on django-odk")
    summary = _("Collection of geolocalized data.")

    return render(request, 'home.html', {'title': title, 'summary': summary})


class OdkGenView(object):

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.object:
            context['title'] = self.object.get_title()
        return context


class XFormListView(generic.ListView):
    model = XForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model._meta.verbose_name_plural
        return context    


class XFormDetailView(OdkGenView, generic.DetailView):
    model = XForm


@login_required(login_url='admin:login')
def xform_upload(request, pk=None):
    template = 'odk/xform_upload.html'
    uploaded_file_url = ''
    obj = None

    context = {
        'title': _("XForm create & load"),
        'pk': pk
    }    

    if pk is not None:
        obj = XForm.objects.get(pk=pk)
        context['uploaded_file_url'] = obj.xml_file.url

    if request.method == 'POST':
        manage_file = ManageFile(request)
        msg, obj = manage_file.process_xform()
        if msg == 'OK':
            context['uploaded_file_url'] = obj.xml_file.url
            messages.success(request, _("XForm loaded"), fail_silently=True)
            return redirect(obj.get_absolute_url())
        else:
            messages.warning(request, msg, fail_silently=True)

    return render(request, template, context)


class XFormDelView(LoginRequiredMixin, generic.DeleteView):
    model = XForm
    template_name = "odk/xform_detail.html"
    confirm_message = _("Delete this form?")
    success_url = reverse_lazy("odk:xform_list")

    def delete(self, request, *args, **kwargs):
        """
        On delete rm file
        """
        self.object = self.get_object()
        try:
            filePath = self.object.xml_file.path
            os.remove(filePath)
        except:
            msg = f"Error while deleting file {filePath}"
            LOG.error(msg)
            messages.warning(self.request, msg, fail_silently=True)
        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)


class XFormSubmitDetailView(LoginRequiredMixin, OdkGenView, generic.DetailView):
    model = XFormSubmit


# @login_required(login_url='admin:login')
def submittedfile_list(request):
    subpath = overwrite_storage.path("XFormSubmit")
    try:
        os.mkdir(subpath)
    except OSError as error:
        pass
    dirs, file_list = overwrite_storage.listdir("XFormSubmit")
    file_set = set(file_list)


    object_list = XFormSubmit.objects.all()
    db_set = set(XFormSubmit.objects.all().values_list('xml_file', flat=True))
    db_setok = {i.replace('XFormSubmit/', '') for i in db_set}

    missing_in_db = list(file_set - db_setok)
    context = {
        'object_list': object_list,
        'missing_in_db': missing_in_db,
        'title': XFormSubmit._meta.verbose_name
    }

    return render(request, 'odk/xformsubmit_list.html', context)


class XFormSubmitDelView(LoginRequiredMixin, generic.DeleteView):
    model = XFormSubmit
    template_name = "odk/xformsubmit_detail.html"
    confirm_message = _("Delete this submitted form?")
    success_url = reverse_lazy("odk:xformsubmit_list")

    def delete(self, request, *args, **kwargs):
        """
        On delete rm file
        """
        self.object = self.get_object()
        
        filePath = self.object.xml_file.path
        try:
            os.remove(filePath) # rm xml
        except:
            pass

        import glob
        filePictureDir = filePath.replace('.xml', '')
        pictures = glob.glob(f"{filePictureDir}/*", recursive=True)
        for pic in pictures:
            try:
                os.remove(pic)
            except OSError as xcpt:
                # msg = f"Error {xcpt} while deleting picture {pic}"
                # LOG.error(msg)
                return render(request, "500.html", {"error_msg": xcpt})
        os.rmdir(filePictureDir)

        success_url = self.get_success_url()
        self.object.delete()
        return HttpResponseRedirect(success_url)

# @login_required(login_url='admin:login')
# def load_submittedfiles(request):
#     """
#     TO_DO: check wether picture can be read here...
#     """
#     dirs, file_list = overwrite_storage.listdir("XFormSubmit")

#     for f in file_list:
#         filepath = os.path.join("XFormSubmit", f)
#         modified_on = overwrite_storage.get_modified_time(filepath)
#         submitted_on = overwrite_storage.get_created_time(filepath)

#         obj = XFormSubmit.objects.create(
#             xml_file=filepath, 
#             submitted_on=submitted_on,
#             modified_on=modified_on
#         )

#     return redirect('odk:xformsubmit_list')
  