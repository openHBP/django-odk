# -*- coding: utf-8 -*-
# utils for xml_content management in XForm & XFormSubmit
import os
import re
import logging

from django.utils.text import get_valid_filename
from django.utils.timezone import now
# Django
from django.utils.translation import gettext as _

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

# form_id is attacker-controlled (parsed from the submitted XML) and is used
# as a directory name: only allow a strict charset, never path separators.
SAFE_FORM_ID = re.compile(r'^[A-Za-z0-9_\-\.]{1,100}$')


def is_safe_form_id(form_id):
    return bool(SAFE_FORM_ID.match(form_id or '')) and form_id not in ('.', '..')


def safe_filename(name):
    """
    Reduce a client-supplied file name to a safe basename.
    Raises SuspiciousFileOperation if nothing usable is left.
    """
    return get_valid_filename(os.path.basename(name or ''))


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

    def process_xformsubmit(self):
        """
        Main function
        return msg, instance
        """
        msg = ''
        instance = None
        msg = self.read_xml(file_key='xml_submission_file')
        if msg == 'OK':
            msg = self.get_key_elements()
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
        - 'xml_file' for template_files (no more used 2022-06-16)
        """
        if self.request.FILES and file_key in self.request.FILES:
            self.xml_content = self.request.FILES[file_key].read().decode("utf-8")
            # LOG_DEBUG.debug(self.xml_content)
            return 'OK'
        else:
            msg = _("File not found")
            LOG.error(msg)
            return msg

    def get_key_elements(self):
        """
        Get key element for processing
        """
        self.form_id = get_form_id(self.xml_content)
        self.version = get_version(self.xml_content)

        if 'ERROR' in [self.form_id, self.version]:
            msg = _("Key elements (form_id - version) not found")
            LOG.error(msg)
            return msg

        if not is_safe_form_id(self.form_id):
            LOG.warning("Rejected ODK submission with invalid form_id=%r", self.form_id)
            return _("Invalid form_id")

        # Only accept submissions for forms actually published on this server
        if not XForm.objects.filter(form_id=self.form_id).exists():
            LOG.warning("Rejected ODK submission for unknown form_id=%r", self.form_id)
            return _("Unknown form_id")

        return 'OK'


    @property
    def submitted_on(self):
        return now().strftime("%Y-%m-%d")


    def get_xform_pk(self, class_name='XForm'):
        """
        Get XForm pk (no more used 2022-06-16)
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


    def save_file(self, file_key, class_name):
        """
        Save file on the server
        """
        try:
            file_pointer = self.request.FILES[file_key]
            filename = safe_filename(file_pointer.name)
            if class_name == "XFormSubmit":
                if not is_safe_form_id(self.form_id):
                    raise ValueError(f"Invalid form_id {self.form_id!r}")
                self.xml_file = os.path.join(class_name, self.form_id, self.submitted_on, filename)
            else:
                self.xml_file = os.path.join(class_name, filename)

            self.xml_filename = os.path.splitext(filename)[0]
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
            picture_files = get_submitted_picture(self.xml_content, 'pic_img')
            # submitted_on = overwrite_storage.get_created_time(self.xml_file)
            instanceid = get_instanceid(self.xml_content)
            try:
                xsub = XFormSubmit.objects.get(instanceid=instanceid)
                # Update
                # xsub.xml_content=xml_pretty_str, # done in models.py on create only!
                xsub.picture_files = picture_files,
                xsub.submitted_on = self.submitted_on
                
            except XFormSubmit.DoesNotExist:
                # Insert
                xsub = XFormSubmit.objects.create(
                    instanceid=instanceid,
                    xml_file=self.xml_file,
                    picture_files=picture_files,
                )
            
            # pathname = self.xml_file
            # lastslash = pathname.rfind('/')
            # fname = pathname[lastslash+1:]
            #msg = f'fichier {fname} submitted!'
            msg = _("Well sent! Thanks!")
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
                        self.form_id,
                        self.submitted_on,
                        self.xml_filename,
                        safe_filename(pic_pointer.name)
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
