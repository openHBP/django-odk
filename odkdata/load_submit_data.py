# -*- coding: utf-8 -*-
import os
import logging

from bs4 import BeautifulSoup

from django.apps import apps
from django.contrib.gis.geos.point import Point
from django.db.models import ManyToOneRel, IntegerField
from django.contrib.gis.db.models import PointField
from django.forms import model_to_dict

from odk.models import XFormSubmit

LOG = logging.getLogger(__name__)


def data_not_in(model, instanceid):
    try:
        model_inst = model.objects.get(instanceid=instanceid)
        return False
    except model.DoesNotExist:
        return True


def load_record(xfs):
    print(f"---------------------")
    print(f"Loading XFormSubmit id: {xfs.id}")

    form_id = xfs.form_id
    model_str = ''.join([i for i in form_id if not i.isdigit()])
    model = apps.get_model('odkdata', model_str.capitalize())
    xfields = ['instanceid']

    if data_not_in(model, xfs.instanceid):

        xfs_dict = model_to_dict(xfs, fields=xfields)

        soup = BeautifulSoup(xfs.xml_content, 'xml')

        fdict = {}
        mdict = {}

        for field in model._meta.get_fields():
            value = None
            fname = field.name
            if fname in xfields:
                value = xfs_dict[fname]
            else:
                if isinstance(field, ManyToOneRel):
                    # Add ManyToOneRel in mdict
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
                            # print(f"{fname}: {value}")
            # Assign value to key in fdict without ManyToOneRel fields
            if not isinstance(field, ManyToOneRel):
                fdict[fname] = value

        # Geometry
        # if fdict['loc_xy'] is not None:
        #     loc_lat, loc_long, loc_alt, precision = fdict['loc_xy'].split(" ")
        #     loc_geom = Point(x=float(loc_long), y=float(loc_lat), srid=4326)
        #     fdict['loc_xy'] = loc_geom

        # Insert data in main model
        try:
            model_inst = model(**fdict)
            model_inst.save()
        except Exception as xcpt:
            LOG.error(xcpt)
            return False

        # Manage ManyToOneRel (mdict)
        keylist = list(mdict.keys())

        for key in keylist:
            print(f"Loading ManyToOneRel {key}")
            obj = apps.get_model('odkdata', key.capitalize())
            # first delete all existing occurences
            obj_qs = obj.objects.filter(**{ model_str: model_inst })
            obj_qs.delete()

            multivalues = mdict[key]
            for values in multivalues:
                values = values.strip("\n") # rm leading and trailing \n
                values_list = values.split("\n")
                
                fields = [i.name for i in obj._meta.get_fields() if i.name not in ('id', model_str)]
                n = 0
                objdict = {}
                for f in fields:
                    try:
                        value = values_list[n]
                    except IndexError:
                        print(f"fields: {fields}")
                        print(f"fields number of items: {len(fields)}")
                        print(f"values_list: {values_list}")
                        print(f"values_list number of items: {len(values_list)}")
                        return

                    objdict[f] = value
                    n += 1
                
                # Add instance of main model
                objdict[model_str] = model_inst

                try:
                    obj_inst = obj(**objdict)
                    obj_inst.save()
                except Exception as xcpt:
                    LOG.error(xcpt)
                    return False
    
    return True
