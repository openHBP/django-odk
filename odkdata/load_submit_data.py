# -*- coding: utf-8 -*-
import os
import logging

from bs4 import BeautifulSoup

from django.apps import apps
from django.db import connection
from django.contrib.gis.geos.point import Point
from django.db.models import ManyToOneRel, IntegerField
from django.contrib.gis.db.models import PointField

from odk.models import XFormSubmit
from odkdata.utils import rm_digit, convert2camelcase


LOG = logging.getLogger(__name__)



def fetch_xml_data(xfs, model):
    """
    params:
    - XFormSubmit instance
    - model object class

    return: fdict, mdict
    """
    soup = BeautifulSoup(xfs.xml_content, 'xml')

    fdict = {}
    mdict = {}

    for field in model._meta.get_fields():
        value = None
        fname = field.name
                    
        if fname == 'instanceid':
            value = xfs.instanceid
        else:
            if isinstance(field, ManyToOneRel):
                itemtag = soup.find_all(fname)
                value = [i.text for i in itemtag]
                mdict[fname] = value                  
            else:
                itemtag = soup.find(fname)
                if itemtag is not None:
                    value = itemtag.text
                    if isinstance(field, IntegerField):
                        if value == '':
                            value = 0
                        value = int(value)
                    if isinstance(field, PointField):
                        loc_lat, loc_long, loc_alt, precision = value.split(" ")
                        value = Point(x=float(loc_long), y=float(loc_lat), srid=4326)

        # Exclude mdict element for fdict assignment
        if fname not in mdict:
            fdict[fname] = value
    return fdict, mdict  



def load_record(xfs):
    """
    params:
    XFormSubmit instance

    return:
        1 success
        -1 python model not found
        -2 db model not found
        0 failure
    """
    LOG.info(f"-----------------------")
    LOG.info(f"Loading XFormSubmit id: {xfs.id}")

    # Init vars
    form_id = xfs.form_id
    pkg_str = rm_digit(form_id).lower()
    model_str = convert2camelcase(rm_digit(form_id))
    
    # Retrieve model objects class
    try:
        model = apps.get_model("odkdata", model_str)
    except LookupError as xcpt:
        return -1, xcpt

    # Check if table exist in DB
    all_tables = connection.introspection.table_names()
    table_name = f"odkdata_{pkg_str}"
    if table_name not in all_tables:
        return -2, f"{table_name} not in database"

    # Fetch data in XML and return fdict and mdict
    fdict, mdict = fetch_xml_data(xfs, model)

    # Upsert data in main model
    model_inst, created = model.objects.get_or_create(instanceid=xfs.instanceid, defaults=fdict)
    try:
        if not created:
            for attr, value in fdict.items(): 
                if attr not in ('id', 'instanceid'):
                    setattr(model_inst, attr, value)
            model_inst.save()
    except Exception as xcpt:
        LOG.error(xcpt)
        return 0, xcpt


    # Manage ManyToOneRel (mdict)
    keylist = list(mdict.keys())
    model_str_lower = model_str.lower()

    for key in keylist:
        LOG.info(f"Loading ManyToOneRel {key}")
        obj = apps.get_model('odkdata', key.capitalize())
        # first delete all existing occurences
        obj_qs = obj.objects.filter(**{ model_str_lower: model_inst })
        obj_qs.delete()

        multivalues = mdict[key]
        for values in multivalues:
            values = values.strip("\n") # rm leading and trailing \n
            values_list = values.split("\n")
            
            fields = [i.name for i in obj._meta.get_fields() if i.name not in ('id', model_str_lower)]
            n = 0
            objdict = {}
            for f in fields:
                try:
                    value = values_list[n]
                except IndexError:
                    LOG.error(f"fields: {fields}")
                    LOG.error(f"fields number of items: {len(fields)}")
                    LOG.error(f"values_list: {values_list}")
                    LOG.error(f"values_list number of items: {len(values_list)}")
                    return 0, f"IndexError between {fields} and {values_list}"

                objdict[f] = value
                n += 1
            
            # Add instance of main model
            objdict[model_str_lower] = model_inst

            try:
                obj_inst = obj(**objdict)
                obj_inst.save()
            except Exception as xcpt:
                LOG.error(xcpt)
                return 0, xcpt
    
    return 1, "OK"
