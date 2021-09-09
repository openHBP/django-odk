# -*- coding: utf-8 -*-
from django.http import Http404
from django.shortcuts import render
from django.utils import timezone

from config.settings import USE_HTTPS
from odk.models import XForm
from odk.openrosa.utils_push import response_with_mimetype_and_name



def rosa_list(request):
    """
    This is where ODK Collect gets its download list.
    xformsList format can be found https://docs.getodk.org/openrosa-form-list/
    """
    # Get all the forms in the DB
    xforms = XForm.objects.all()

    # Prepare context to send back
    PROTOCOL = 'https' if USE_HTTPS else 'http'
    context = {
        'host': f"{PROTOCOL}://{request.get_host()}",
        'object_list': xforms,
    }

    # Sending back the datas with the xformslist format
    response = render(
        request,
        "xformsList.xml",
        context,
        content_type="text/xml; charset=utf-8"
    )
    response['X-OpenRosa-Version'] = '1.0'
    response['Date'] = timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z')
    return response


def rosa_detail(request, form_id):
    """
    Download XForm XML view.
    """
    try:
        obj = XForm.objects.get(form_id=form_id)
    except XForm.DoesNotExist:
        return Http404("XForm does not exist.")

    response = response_with_mimetype_and_name('xml', form_id, show_date=False)
    response.content = obj.xml_content
    return response
