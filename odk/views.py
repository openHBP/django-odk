# -*- coding: utf-8 -*-
import os
import logging

from braces.views import LoginRequiredMixin
# django modules
from django.utils.translation import gettext as _
from django.utils.timezone import now
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.views import generic
from django.shortcuts import render, redirect
from django.contrib import messages
from django.http import HttpResponseRedirect
# odk modules
from .storage import overwrite_storage
from .models import XForm, XFormSubmit, xform_path
from .forms import OdkForm
from .admin import xformsubmit_return_message
# odkdata modules
from odkdata import create_model, load_submit_data
from odkdata.utils import rm_digit, convert2camelcase


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


class XFormTemplateView(generic.TemplateView):
    template_name = "xform_doc.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = _("XForm Documentation")
        return context


class XFormListView(generic.ListView):
    model = XForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.model._meta.verbose_name_plural
        return context    


class XFormDetailView(OdkGenView, generic.DetailView):
    model = XForm

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        if 'xls2xml' in request.path:
            obj.process_xform()
            obj.save()
            messages.success(request, _("XLSX successfully converted to XML XForm format."))
        if 'createmodel' in request.path:
            if create_model.process(obj):
                model_name = create_model.rm_digit(obj.form_id).capitalize()
                create_msg = _("created with success!")
                messages.success(request, f"Model odkdata.models.{model_name} {create_msg}")
                messages.info(request, _("You can now run 'manage.py makemigrations odkdata' then 'manage.py migrate'."))
                obj.model_created_on = now()
                obj.save()
                return redirect(obj.get_absolute_url())
            else:
                messages.error(request, "Error while creating model, check your error logs.")

        return super().get(request, *args, **kwargs)


@login_required(login_url='admin:login')
def xform_upload(request, pk=None):
    """Xform upload"""
    template = 'odk/xform_upload.html'
    uploaded_file_url = None
    obj = None
        
    if pk is not None:
        obj = XForm.objects.get(pk=pk)
        uploaded_file_url = obj.xml_file.url

    if request.method == 'POST' and request.FILES.get('xls_file'):
        file_pointer = request.FILES.get('xls_file')
        file_path = os.path.join("XForm", file_pointer.name)
        
        filename = overwrite_storage.save(file_path, file_pointer)

        uploaded_file_url = overwrite_storage.url(filename)

        obj = XForm.objects.create(xls_file=file_path, created_by=request.user, form_id=f"{filename} (tmp)")
        obj.save()
        # messages.success(request, _("xlsx file loaded"), fail_silently=True)
        return redirect(obj.get_absolute_url())

    context = {
        'form': OdkForm(data=request.POST, files=request.FILES, instance=obj),
        'title': _("XForm create & load"),
        'pk': pk,
        'uploaded_file_url': uploaded_file_url
    }

    return render(request, template, context)


class XFormDelView(LoginRequiredMixin, generic.DeleteView):
    model = XForm
    template_name = "odk/xform_detail.html"
    confirm_message = _("Delete this form?")
    success_url = reverse_lazy("odk:xform_list")

    def form_valid(self, form):
        """
        On delete rm xls and xml file
        """
        try:
            if self.object.xls_file:
                filePath = self.object.xls_file.path
                os.remove(filePath)
            if self.object.xml_file:
                filePath = self.object.xml_file.path
                os.remove(filePath)
        except Exception as e:
            msg = f"Error while deleting file {filePath}"
            LOG.error(msg)
            messages.warning(self.request, msg, fail_silently=True)
        self.object.delete()
        success_url = self.get_success_url()
        return HttpResponseRedirect(self.success_url)


class XFormSubmitDetailView(LoginRequiredMixin, OdkGenView, generic.DetailView):
    model = XFormSubmit

    def get(self, request, *args, **kwargs):
        obj = self.get_object()

        if 'loaddata/' in request.path:
            return_value, message = load_submit_data.load_record(obj)
            
            xformsubmit_return_message(return_value, message, request, obj)

        return super().get(request, *args, **kwargs)   


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

  