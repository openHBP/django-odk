# -*- coding: utf-8 -*-
import os
import logging

from django.http.response import HttpResponse
from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.utils import timezone
from django.template import loader

from odk.models import XFormSubmit
from odk.utils import ManageFile

LOG_DEBUG = logging.getLogger("mydebug")


class BaseOpenRosaResponse(HttpResponse):
    """
    OpenRosa settings
    """
    status_code = 201
    def __init__(self, *args, **kwargs):
        super(BaseOpenRosaResponse, self).__init__(*args, **kwargs)
        self.setdefault('X-OpenRosa-Version', '1.0')
        self.setdefault('Date', timezone.now().strftime('%a, %d %b %Y %H:%M:%S %Z'))
        self.setdefault('X-OpenRosa-Accept-Content-Length', 10000000)
        self.setdefault('Content-Type', 'text/xml; charset=utf-8')


@csrf_exempt
def xform_submit(request, username=None):
    """
    Function used to manage the submissions and the responses. 
    """    
    if request.method == 'HEAD':
        """
        We are waiting the HEAD request, that is sent by ODK Collect
        to check the server configuration before sending the POST request.
        Collect expects 1 information as reponse to a HEAD request:
        Status code = 204
        """
        response = BaseOpenRosaResponse(status=204)
        # Keep base_url and add /submission
        response['Location'] = request.build_absolute_uri().replace(
            request.get_full_path(), '/odk/submission')
        return response
        
    
    if request.method == 'POST':
        """
        Just save submitted xml forms in overwrite_storage
        ODK needs two things for a form to be considered successful
        1. status code 201 (created).
        2. location header with absolute_uri
        """
        data = {}
    
        subfile = ManageFile(request)
        msg, xsub = subfile.process_xformsubmit()

        data['message'] = msg
        data['encrypted'] = False

        if xsub is None:
            status_code = 404
        else:
            status_code = 201
            data['formid'] = xsub.form_id
            data['instanceID'] = xsub.instanceid
            data['submissionDate'] = xsub.submitted_on
            data['markedAsCompleteDate'] = xsub.submitted_on

        # Building response with XML template and data dict
        response = BaseOpenRosaResponse(loader.get_template('submission.xml').render(data))
        response.status_code = status_code

    return response


