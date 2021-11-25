# -*- coding: utf-8 -*-
# utils for xml_content management in XForm & XFormSubmit
import os
import re
import logging
# import xml.dom.minidom
from datetime import datetime
# Django
from django.utils.translation import ugettext as _
from django.db import IntegrityError
# App
from odk.storage import overwrite_storage
from odk.models import (
    XForm, XFormSubmit, 
    get_form_id,
    get_version,
    get_survey_date,
    get_instanceid
)

LOG = logging.getLogger(__name__)
LOG_DEBUG = logging.getLogger('mydebug')


def get_submitted_picture(xml_content, picture_tag):
    """
    Search picture_tag
    """
    matches = None
    my_regexp = re.compile(r'<{picture_tag}>([^<]+)</{picture_tag}>'.format(picture_tag=picture_tag))
    matches = my_regexp.findall(xml_content)
    return matches


class ManageFile(object):
    """
    Abstract class for XML file read & save
    and data insert/update in XForm & XFormSubmit tables
    """
    request = None
    xml_content = ''
    form_id = ''
    version = ''
    xml_file = ''
    xml_filename = ''
    xform = None

    def __init__(self, request):
        self.request = request

    def process_xform(self):
        """
        Main function
        return msg, instance
        """
        msg = ''
        instance = None
        msg = self.read_xml(file_key='xml_template_file')
        if msg == 'OK':
            msg = self.set_key_elements()
            if msg == 'OK':
                msg = self.save_file(file_key='xml_template_file', class_name='XForm')
                if msg == 'OK':
                    msg = self.get_xform_pk(class_name='XForm')
                    if msg == 'NOT_FOUND':
                        msg, instance = self.insert_in_xform()                           
                    if msg == 'FOUND':
                        msg, instance = self.update_in_xform()

        return msg, instance

    def process_xformsubmit(self):
        """
        Main function
        return msg, instance
        """
        msg = ''
        instance = None
        msg = self.read_xml(file_key='xml_submission_file')
        if msg == 'OK':
            msg = self.set_key_elements()
            if msg == 'OK':
                # msg = self.get_xform_pk(class_name='XFormSubmit')
                # if msg == 'FOUND':
                msg = self.save_file(file_key='xml_submission_file', class_name='XFormSubmit')
                if msg == 'OK':
                    msg = self.save_pictures()
                    if msg == 'OK':
                        msg, instance = self.insert_in_xformsubmit()                      

        return msg, instance

    def read_xml(self, file_key):
        """
        Get file and read content
        file_key:
        - 'xml_submission_file' for submitted files
        - 'xml_template_file' for template_files
        """
        if self.request.FILES and file_key in self.request.FILES:
            self.xml_content = self.request.FILES[file_key].read().decode("utf-8")
            # LOG_DEBUG.debug(self.xml_content)
            return 'OK'
        else:
            msg = _("File not found")
            LOG.error = msg
            return msg

    def set_key_elements(self):
        """
        Get key element for processing
        """
        self.form_id = get_form_id(self.xml_content)
        self.version = get_version(self.xml_content)

        if 'ERROR' in [self.form_id, self.version]:
            msg = _("Key elements (form_id - version) not found")
            LOG.error = msg
        else:
            msg = 'OK'
        # print(f"form_id: {self.form_id}")
        # print(f"version: {self.version}")
        return msg

    @property
    def subfolder1(self):
        return f"{self.form_id}-{self.version}"

    @property
    def subfolder2(self):
        survey_date = get_survey_date(self.xml_content)
        if survey_date is None:
            survey_date = datetime.now().strftime("%Y-%m-%d")
        return survey_date

    def get_xform_pk(self, class_name='XForm'):
        """
        Get XForm pk
        """
        try:
            self.xform = XForm.objects.get(form_id=self.form_id, version=self.version)
            msg = 'FOUND'
        except XForm.DoesNotExist:
            if class_name == 'XFormSubmit':
                msg = f"form_id: {self.form_id} - version: {self.version} DoesNotExist in XForm!!!"
                LOG.error(msg)
            else:
                msg = 'NOT_FOUND'
        return msg

    def update_in_xform(self):
        """
        Update xform table with new template values
        Need to have variable 'self.xml_file' => save_file before!
        """
        try:
            self.xform.xml_content = self.xml_content
            self.xform.xml_file = self.xml_file
            self.xform.modified_on = overwrite_storage.get_modified_time(self.xml_file)
            self.xform.submitted_on = overwrite_storage.get_created_time(self.xml_file)
            self.xform.save()

        except Exception as xcpt:
            LOG.error(xcpt)            
            return xcpt, None
        return 'OK', self.xform

    def save_file(self, file_key, class_name):
        """
        Save file on the server
        """
        try:
            file_pointer = self.request.FILES[file_key]
            if class_name == "XFormSubmit":
                self.xml_file = os.path.join(class_name, self.subfolder1, self.subfolder2, file_pointer.name)
            else:
                self.xml_file = os.path.join(class_name, file_pointer.name)
            
            self.xml_filename = file_pointer.name.replace('.xml', '')
            overwrite_storage.save(self.xml_file, file_pointer)
            msg = 'OK'
        except Exception as xcpt:
            LOG.error(xcpt)
            msg = xcpt
        return msg        

    def insert_in_xformsubmit(self):
        """
        Insert submitted data into XFormSubmit table
        Must be last fucntion call!
        """
        try:
            # myxml = xml.dom.minidom.parseString(self.xml_content)
            # xml_pretty_str = myxml.toprettyxml()
            picture_files = get_submitted_picture(self.xml_content, f'pic_img')
            modified_on = overwrite_storage.get_modified_time(self.xml_file)
            submitted_on = overwrite_storage.get_created_time(self.xml_file)
            instanceid = get_instanceid(self.xml_content)
            try:
                xsub = XFormSubmit.objects.get(instanceid=instanceid)
                # Update
                # xsub.xml_content=xml_pretty_str, # done in models.py
                xsub.picture_files = picture_files,
                xsub.modified_on = modified_on
                xsub.submitted_on = submitted_on
                
            except XFormSubmit.DoesNotExist:
                # Insert
                xsub = XFormSubmit.objects.create(
                    # xform=self.xform,
                    xml_file=self.xml_file,
                    # xml_content=xml_pretty_str, # done in models.py
                    picture_files=picture_files,
                    submitted_on=submitted_on,
                    modified_on=modified_on
                )
            
            pathname = self.xml_file
            lastslash = pathname.rfind('/')
            fname = pathname[lastslash+1:]
            msg = f'fichier {fname} submitted!'
        except Exception as xcpt:
            LOG.error(xcpt)
            return xcpt, None
        return msg, xsub


    def save_pictures(self):
        """
        Save file on the server
        Only for submitted files
        """
        try:
            picture_files = get_submitted_picture(self.xml_content, f'pic_img')
            for picture_file in picture_files:
                
                if picture_file in self.request.FILES:
                    pic_pointer = self.request.FILES[picture_file]
                    # LOG_DEBUG.debug(f'pic_pointer: {pic_pointer}')
                    pic_path = os.path.join(
                        "XFormSubmit",
                        self.subfolder1,
                        self.subfolder2,
                        self.xml_filename,
                        pic_pointer.name
                    )
                    # LOG_DEBUG.debug(f"pic_path={pic_path}")
                    overwrite_storage.save(pic_path, pic_pointer)
                # else:
                #     LOG_DEBUG.debug('FILE NOT IN request')
                #     LOG_DEBUG.debug(self.request.FILES)
            msg = 'OK'
        except Exception as xcpt:
            LOG.error(xcpt)
            msg = xcpt
        return msg


    def insert_in_xform(self):
        """
        in: filename (str) and user (instance)
        out: XForm instance
        """
        try:
            # myxml = xml.dom.minidom.parseString(self.xml_content)
            # xml_pretty_str = myxml.toprettyxml()
            obj = XForm.objects.create(
                xml_file=self.xml_file,
                # xml_content=xml_pretty_str, # done in models.py
                created_by=self.request.user,
                modified_by=self.request.user
            )
        except IntegrityError as integr:
            # should not happen since we've done a check on form_id & version in get_xform_pk
            LOG.error(integr)
            return integr, None
            
        except Exception as xcpt:
            LOG.error(xcpt)
            return xcpt, None

        return 'OK', obj



