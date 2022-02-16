# -*- coding: utf-8 -*-
import re
import os
import logging
import xml.dom.minidom

from hashlib import md5
from datetime import datetime

from django.db import models
from django.utils.translation import ugettext as _
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
        help_text="XLSForm "+_("converted by")+" <a href='https://getodk.org/xlsform/' target='_blank'>https://getodk.org/xlsform/</a>"
    )
    xml_content = models.TextField(
        verbose_name=_("Content of XML form")
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
        on_delete=models.CASCADE, verbose_name=_("Created by")
    )
    created_on = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created on")
    )
    modified_by = models.ForeignKey(
        Profile,
        related_name="xform_modified_by",
        on_delete=models.CASCADE,
        verbose_name=_("Modified by")
    )
    modified_on = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Modified on")
    )

    class Meta:
        verbose_name = _("Available form")
        unique_together = ('form_id', 'version')
        ordering = ('xml_file',)

    @property
    def class_name(self):
        return self.__class__.__name__

    def _set_xml_content(self):
        with open(self.xml_file.path, 'r') as f:
            myxml = xml.dom.minidom.parseString(f.read())
            self.xml_content = myxml.toprettyxml()
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

    def save(self, *args, **kwargs):
        """
        Save form_id, version and title contained in xml file
        """
        self._set_xml_content()
        old_form_id = self.form_id
        self._set_form_id()
        self._set_version()
        self._set_title()
        # check if we have an existing form_id,
        # if so, the one must match but only if xform is NOT new
        if self.pk and old_form_id and old_form_id != self.form_id:
            raise Exception(
                "Your updated form's form_id '%(new_id)s' must match "
                  "the existing forms' form_id '%(old_id)s'." %
                  {'new_id': self.form_id, 'old_id': old_form_id})

        super(XForm, self).save(*args, **kwargs)
        return

    def get_absolute_url(self):
        return reverse('odk:xform_detail', args=[str(self.id)])

    def get_title(self):
        return self._meta.verbose_name

    def __str__(self):
        filename = str(self.xml_file).replace(f"{self.class_name}/", '')
        form_id = getattr(self, 'form_id', '')
        version = getattr(self, 'version', '')
        form_version = f"{filename} => {form_id}, version {version}"
        return form_version

    @property
    def hash(self):
        return u'md5:%s' % md5(self.xml_content.encode('utf8')).hexdigest()


#############################################################

def submission_path(instance, filename):
    """
    Define where to save posted xforms
    """
    path = os.path.join(
        instance.class_name,
        instance.subfolder1,
        instance.subfolder2,
        os.path.split(filename)[1]
    )
    return path


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
        verbose_name=_("Submitted on")
    )
    modified_by = models.CharField(
        max_length=255,
        verbose_name=_("Modified by"),
        blank=True, null=True
    )
    modified_on = models.DateTimeField(
        auto_now=True, verbose_name=_("Modified on")
    )

    class Meta:
        verbose_name = _("Submitted form")
        # unique_together = ('form_id', 'version', 'instanceid')
        ordering = ('submitted_on',)

    @property
    def class_name(self):
        return self.__class__.__name__

    @property
    def subfolder1(self):
        return f"{self.form_id}-{self.version}"

    @property
    def subfolder2(self):
        return self.survey_date

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
            self.survey_date = datetime.now().strftime("%Y-%m-%d")

    def _set_username(self):
        matches = re.findall(r'<username>([^<]+)</username>', self.xml_content)
        if matches:
            self.submitted_by = matches[0]
            if self.modified_by is None:
                self.modified_by = self.submitted_by
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
        """
        Get pictures in the appropriate folder, ie:
        pic_path = os.path.join(
                        "XFormSubmit",
                        subfolder1 (form_id-version),
                        subfolder2 (date as yyyy-mm-dd),
                        xml_filename,
                        pic_pointer.name
                    )
        """
        url_path = self.xml_file.url.replace('.xml', '/')
        return url_path

    def save(self, *args, **kwargs):
        """
        Save form_id, instanceid contained in xml file
        """
        self._set_xml_content()
        self._set_form_id()
        self._set_version()
        self._set_survey_date()
        self._set_username()
        self._set_deviceid()
        old_instanceid = self.instanceid
        self._set_instanceid()
        # check if we have an existing instanceid,
        # if so, the one must match but only if xformsubmit is NOT new
        if self.pk and old_instanceid and old_instanceid.__str__() != self.instanceid:
            raise Exception(
                f"Your updated form's instanceid '{self.instanceid}' must match the existing forms' instanceid '{old_instanceid}'."
                  )

        super(XFormSubmit, self).save(*args, **kwargs)
        return

    def get_absolute_url(self):
        return reverse('odk:xformsubmit_detail', args=[str(self.id)])

    def get_title(self):
        return self._meta.verbose_name

    def __str__(self):
        return self.xml_file.name
