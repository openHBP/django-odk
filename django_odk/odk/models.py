# -*- coding: utf-8 -*-
import re
import os
import logging
import xml.dom.minidom

from pyxform.xls2xform import xls2xform_convert

from hashlib import md5
from django.utils.timezone import now

from django.db.models.signals import post_save
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.urls import reverse
from django.contrib.auth import get_user_model

Profile = get_user_model()

__author__ = 'jean pierre huart, patrick houben'
__email__ = 'j.huart@cra.wallonie.be, p.houben@cra.wallonie.be'
__copyright__ = 'Copyright 2021, Jean Pierre Huart, Patrick Houben'
__license__ = 'GPLv3'
__date__ = '2021-03-05'
__version__ = '0.1 dev'
__status__ = 'Development'


LOG = logging.getLogger(__name__)
LOG_DEBUG = logging.getLogger('mydebug')


def xform_path(instance, filename):
    """
    Define where to save posted xforms
    """
    my_xform_path = os.path.join(
        instance.class_name,
        os.path.split(filename)[1]
    )
    return my_xform_path


def get_form_id(xml_content):
    """
    Search id attr in data tag
    """
    my_regexp = re.compile(r'<data.*id="([^"]+)"', re.DOTALL)
    matches = my_regexp.findall(xml_content)
    if matches:
        return matches[0]
    else:
        LOG.error(f"Unable to find 'id attr' of <data> tag in xml file")
        return 'ERROR'


def get_version(xml_content):
    """
    Search version attr in data tag in XML and set it in table
    """
    my_regexp = re.compile(r'<data.*version="([^"]+)"', re.DOTALL)
    matches = my_regexp.findall(xml_content)
    if matches:
        return matches[0]
    else:
        # Version might not be present in settings tab or tab is missing!
        return get_form_id(xml_content)


class XForm(models.Model):
    """
    XForm management
    necessary steps through admin
    1. Build an XLSForm file https://xlsform.org/en/
    2. Submit this file on https://getodk.org/xlsform/
    3. Check file correctness while clicking on 'Preview in browser' button
    4. Copy-paste XML content generated in xml_content field
    => The file is ready to read in ODK Collect app
    """
    xls_file = models.FileField(
        verbose_name=_("Excel file"),
        upload_to=xform_path,
        blank=True, null=True,
        help_text=_("XLSForm with 3 tabs: survey, choices, settings")
    )
    xml_file = models.FileField(
        verbose_name=_("XML file"),
        upload_to=xform_path,
        blank=True, null=True,
        help_text="XLSForm "+_("converted by")+" <a href='https://getodk.org/xlsform/' target='_blank'>https://getodk.org/xlsform/</a>"
    )
    xml_content = models.TextField(
        verbose_name=_("Content of XML form"),
        blank=True, null=True,
    )
    form_id = models.SlugField(
        editable=False,
        max_length=200,
        help_text=_("Retrieved from XLSForm (xls settings tab)")
    )
    version = models.CharField(
        editable=False,
        max_length=200,
        help_text=_("Retrieved from XLSForm (xls settings tab)")
    )
    title = models.CharField(
        verbose_name=_("Title"),
        editable=False, max_length=250,
        help_text=_("Retrieved from XLSForm (xls settings tab)")
    )
    short_desc = models.CharField(
        max_length=250,
        verbose_name=_("Short description"),
        blank=True
    )
    created_by = models.ForeignKey(
        Profile,
        related_name="xform_created_by",
        on_delete=models.CASCADE, verbose_name=_("Created by"),
        blank=True, null=True,
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created on")
    )
    model_created_on = models.DateTimeField(
        verbose_name=_("Model created on"),
        null=True, blank=True
    )

    class Meta:
        verbose_name = _("Available form")
        unique_together = ('form_id', 'version')
        ordering = ('xml_file',)

    @property
    def class_name(self):
        return self.__class__.__name__

    def _set_creator(self, current_user):
        if not self.created_by:
            self.created_by = current_user

    def _set_xml_content(self):
        try:
            with open(self.xml_file.path, 'r') as f:
                # myxml = xml.dom.minidom.parseString(f.read())
                # self.xml_content = myxml.toprettyxml()
                self.xml_content = f.read()
        except Exception as xcpt:
            raise Exception(f"XML file not found in {self.xml_file.path}")
        return

    def _set_form_id(self):
        """
        Search over <instance> tag in xml content and store id
        """
        my_regexp = re.compile(r'<instance>.*?id="([^"]+)".*</instance>',
                               re.DOTALL)
        match = my_regexp.findall(self.xml_content)
        if match:
            self.form_id = match[0]
            return True
        else:
            return False

    def _set_version(self):
        """
        Search over <instance> tag in xml content and store version
        """
        my_regexp = re.compile(r'<instance>.*?version="([^"]+)".*</instance>',
                               re.DOTALL)
        matches = my_regexp.findall(self.xml_content)
        if matches:
            self.version = matches[0]
        else:
            self.version = self.form_id
        return

    def _set_title(self):
        """
        Search over <h:title> tag in xml content and store form title
        \s+ => any white space character
        ^ => beginning
        $ => end
        """
        text = re.sub(r'\s+', ' ', self.xml_content)
        matches = re.findall(r'<h:title>([^<]+)</h:title>', text)
        if len(matches) != 1:
            raise Exception('There should be a single title.', matches)
        self.title = '' if not matches else matches[0]
        return

    def process_xform(self):
        xlspath = self.xls_file.path
        xmlpath = xlspath.replace(".xlsx", ".xml")
        response = xls2xform_convert(xlspath, xmlpath)
        # TODO: to be improved!
        if response:
            raise Exception(response)
        else:
            self.xml_file = self.xls_file.name.replace(".xlsx", ".xml")
            self._set_xml_content()
            self._set_form_id()
            self._set_version()
            self._set_title()
        return

    def get_absolute_url(self):
        return reverse('odk:xform_detail', args=[str(self.id)])

    def get_title(self):
        return self._meta.verbose_name

    def __str__(self):
        filename = str(self.xls_file).replace(f"{self.class_name}/", '')
        form_id = getattr(self, 'form_id', '')
        version = getattr(self, 'version', '')
        form_version = f"{form_id} {version}"
        return filename

    @property
    def hash(self):
        return u'md5:%s' % md5(self.xml_content.encode('utf8')).hexdigest()


#############################################################

def get_survey_date(xml_content):
    matches = re.findall(r'<today>([^<]+)</today>', xml_content)
    if matches:
        return matches[0]
    else:
        return None


def get_instanceid(xml_content):
    """
    unique identifier per survey
    """
    matches = re.findall(r'<instanceID>uuid:([^<]+)</instanceID>', xml_content)
    if matches:
        return matches[0]
    else:
        LOG.error("Unable to find '<instanceID>uuid:' pattern in xml file")
        return None


class XFormSubmit(models.Model):
    """
    Submitted files from ODK Collect
    xformsubmit pictures location is xml_file location as directory
    used in odkdata.load_submit_data and odk.utils.ManageFile.save_pictures
    """
    # xform = models.ForeignKey(
    #     XForm,
    #     on_delete=models.PROTECT,
    #     verbose_name="Template form",
    #     related_name="template_form"
    # )
    form_id = models.SlugField(
        editable=False,
        max_length=200,
        help_text=_("Retrieved from XML form (settings tab of Excel file)")
    )
    version = models.CharField(
        editable=False,
        max_length=200,
        help_text=_("Retrieved from XML form (settings tab of Excel file)")
    )
    instanceid = models.UUIDField(unique=True)
    deviceid = models.CharField(
        max_length=255,
        blank=True, null=True
    )
    survey_date = models.DateField(
        verbose_name=_("Encoding date"),
        blank=True, null=True
    )
    picture_files = models.JSONField(
        verbose_name=_("Picture file names"),
        blank=True, null=True
    )
    xml_file = models.FileField(
        verbose_name=_('Submitted form'),
        help_text=_("XML file sended through ODK Collect Mobile App"),
        blank=True
    )
    xml_content = models.TextField(
        verbose_name=_("Content of XML file submitted"),
        help_text=_("XML content sended through ODK Collect Mobile App")
    )
    submitted_by = models.CharField(
        max_length=255,
        verbose_name=_("Submitted by"),
        blank=True, null=True
    )
    submitted_on = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Submitted on")
    )
    inserted_on = models.DateTimeField(
        verbose_name=_("Inserted on"),
        blank=True, null=True
    )    

    class Meta:
        verbose_name = _("Submitted form")
        verbose_name_plural = _("Submitted forms")
        ordering = ('submitted_on',)

    @property
    def class_name(self):
        return self.__class__.__name__

    def _set_xml_content(self):
        with open(self.xml_file.path, 'r') as f:
            myxml = xml.dom.minidom.parseString(f.read())
            self.xml_content = myxml.toprettyxml()        
        # x = etree.parse(self.xml_file.path)
        # self.xml_content = etree.tostring(x, pretty_print=True, encoding=str)
        return

    def _set_form_id(self):
        self.form_id = get_form_id(self.xml_content)

    def _set_version(self):
        self.version = get_version(self.xml_content)

    def _set_survey_date(self):
        self.survey_date = get_survey_date(self.xml_content)
        if self.survey_date is None:
            self.survey_date = now().strftime("%Y-%m-%d")

    def _set_username(self):
        matches = re.findall(r'<username>([^<]+)</username>', self.xml_content)
        if matches:
            self.submitted_by = matches[0]
            return
        else:
            LOG.warning("Unable to find '<username>' pattern in xml file")
            return

    def _set_deviceid(self):
        matches = re.findall(r'<deviceid>([^<]+)</deviceid>', self.xml_content)
        if matches:
            self.deviceid = matches[0]
            return
        else:
            LOG.warning("Unable to find '<deviceid>' pattern in xml file")
            return

    def _set_instanceid(self):
        self.instanceid = get_instanceid(self.xml_content)

    def rm_xmlext_from_url(self):
        url_path = self.xml_file.url.replace('.xml', '/')
        return url_path

    def get_absolute_url(self):
        return reverse('odk:xformsubmit_detail', args=[str(self.id)])

    def get_title(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.xml_file.name


#################
# SIGNALS
#################

def fillin_xml_fields(instance, created, **kwargs):
    """
    based on xml file uploaded, fillin form_id, version, xml_content, username and instanceid
    done in post_save signal with created flag in order to allow modification in Db via Django Admin
    """    
    if created:
        try:
            instance._set_xml_content()
            instance._set_form_id()
            instance._set_version()
            instance._set_survey_date()
            instance._set_username()
            instance._set_instanceid()
            instance.save()
        except Exception as xcpt:
            raise Exception(xcpt)

post_save.connect(receiver=fillin_xml_fields, sender=XFormSubmit, weak=False)